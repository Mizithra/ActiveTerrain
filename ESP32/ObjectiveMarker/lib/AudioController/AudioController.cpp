#include "AudioController.h"


// Forward declare the notification class so we can reference the main object safely
class Mp3Notify;

// --- DFPlayer Mini Configuration (UART2 Pins 16 & 17) ---
// ESP32 HardwareSerial 2 defaults: RX2 = GPIO 16, TX2 = GPIO 17
#define FPS_RX 16
#define FPS_TX 17


// Tunable constants, pulled out of the logic below so hardware quirks can
// be adjusted here without hunting through playback code.
namespace {
  constexpr uint16_t DEFAULT_VOLUME        = 20;  // lower baseline, insulates clone chip against brownouts
  constexpr uint32_t VOLUME_SETTLE_MS      = 500; // critical delay for AB250S330Y to settle command registry
  constexpr UBaseType_t AUDIO_QUEUE_LENGTH = 8;
}


// Target Serial2 globally to align with Pins 16 & 17
AudioController::AudioController()
  : _serial(2), _mp3(_serial) {}   // UART2, matches your FPS_RX/FPS_TX pins

AudioController::~AudioController() {
  if (taskHandle != nullptr) {
    vTaskDelete(taskHandle);
  }
  if (commandQueue != nullptr) {
    vQueueDelete(commandQueue);
  }
}

void AudioController::begin(const String &objectiveTopic) {
  _topic = objectiveTopic + "/audio_control";

  if (taskHandle != nullptr) {
    return;
  }

  commandQueue = xQueueCreate(AUDIO_QUEUE_LENGTH, sizeof(AudioCommandRequest));
  if (commandQueue == nullptr) {
    Serial.println(F("AudioController: failed to create command queue"));
    return;
  }

  BaseType_t taskCreated = xTaskCreatePinnedToCore(
      audioTaskEntry,
      "AudioTask",
      4096,
      this,
      1,
      &taskHandle,
      1
  );
  if (taskCreated != pdPASS) {
    taskHandle = nullptr;
    vQueueDelete(commandQueue);
    commandQueue = nullptr;
    Serial.println(F("AudioController: failed to create audio task"));
  }
}

// ============================================================================
// MQTT / business logic
// Purely about interpreting the incoming message. No serial/DFPlayer
// access -- this could be unit tested without any hardware attached.
// ============================================================================

// Maps a JSON "command" string to an AudioCommand. Unknown or missing
// names fall back to AudioCommand::UNKNOWN.
AudioCommand AudioController::commandFromString(const String &name) {
  if (name == "play_track") return AudioCommand::PLAY_TRACK;
  if (name == "play_next")  return AudioCommand::PLAY_NEXT;
  if (name == "play_prev")  return AudioCommand::PLAY_PREV;
  if (name == "pause")      return AudioCommand::PAUSE;
  if (name == "resume")     return AudioCommand::RESUME;
  if (name == "stop")       return AudioCommand::STOP;
  if (name == "start_over") return AudioCommand::START_OVER;
  return AudioCommand::UNKNOWN;
}

// Accepts either {"command": "play_track", "track": 3} JSON, or a bare
// numeric string (e.g. "3") as a "play this track" shorthand. Anything
// else comes back as AudioCommand::UNKNOWN.
AudioCommandRequest AudioController::parseMqttPayload(const String &payload) {
  AudioCommandRequest req;

  JsonDocument doc; // ArduinoJson v7
  DeserializationError err = deserializeJson(doc, payload);

  if (!err && doc["command"].is<const char *>()) {
    req.command = commandFromString(String((const char *)doc["command"]));
    req.track = doc["track"] | 0;
  } else if (payload.length() > 0 && payload.toInt() > 0) {
    req.command = AudioCommand::PLAY_TRACK;
    req.track = payload.toInt();
  }
  // else: leaves req.command == AudioCommand::UNKNOWN (the struct's default)

  return req;
}

void AudioController::handleMqttEvent(const String &topic, const String &payload) {
  AudioCommandRequest req = parseMqttPayload(payload);
  Serial.printf("AudioController: command=%d track=%d (raw payload: '%s')\n",
                (int)req.command, req.track, payload.c_str());
  enqueueCommand(req);
}

// The only place that maps command requests to task-owned player operations.
void AudioController::executeCommand(const AudioCommandRequest &req) {
  switch (req.command) {
    case AudioCommand::PLAY_TRACK: playTrackNow(req.track); break;
    case AudioCommand::PLAY_NEXT:  playTrackNow(_currentTrack + 1); break;
    case AudioCommand::PLAY_PREV:  playTrackNow(_currentTrack - 1); break;
    case AudioCommand::PAUSE:      pauseNow(); break;
    case AudioCommand::RESUME:     resumeNow(); break;
    case AudioCommand::STOP:       stopNow(); break;
    case AudioCommand::START_OVER: startOverNow(); break;
    case AudioCommand::UNKNOWN:
    default:
      Serial.println(F("AudioController: unrecognized command, ignoring"));
      break;
  }
}

void AudioController::enqueueCommand(const AudioCommandRequest &req) {
  if (commandQueue == nullptr) {
    Serial.println(F("AudioController: command queue is unavailable"));
    return;
  }
  if (xQueueSend(commandQueue, &req, 0) != pdTRUE) {
    Serial.println(F("AudioController: command queue full, dropping command"));
  }
}

void AudioController::audioTaskEntry(void *param) {
  static_cast<AudioController *>(param)->audioTaskLoop();
}

void AudioController::audioTaskLoop() {
  _mp3.begin();
  Serial.println(F("AudioController: DFPlayer initialized"));

  AudioCommandRequest req;
  for (;;) {
    _mp3.loop();
    if (xQueueReceive(commandQueue, &req, pdMS_TO_TICKS(20)) == pdTRUE) {
      executeCommand(req);
    }
  }
}

// ============================================================================
// Playback control API -- one function per command.
// ============================================================================

void AudioController::playTrack(int track) {
  AudioCommandRequest req;
  req.command = AudioCommand::PLAY_TRACK;
  req.track = track;
  enqueueCommand(req);
}

void AudioController::playTrackNow(int track) {
  primeDfPlayer();

  Serial.printf("AudioController: playing track %d\n", track);
  _mp3.playMp3FolderTrack(track);

  _currentTrack = track;
  signalPlaybackStarted();
}

void AudioController::playNext() {
  AudioCommandRequest req;
  req.command = AudioCommand::PLAY_NEXT;
  enqueueCommand(req);
}

void AudioController::playPrev() {
  AudioCommandRequest req;
  req.command = AudioCommand::PLAY_PREV;
  enqueueCommand(req);
}

void AudioController::pause() {
  AudioCommandRequest req;
  req.command = AudioCommand::PAUSE;
  enqueueCommand(req);
}

void AudioController::pauseNow() {
  Serial.println(F("AudioController: pause"));
  _mp3.pause();
}

void AudioController::resume() {
  AudioCommandRequest req;
  req.command = AudioCommand::RESUME;
  enqueueCommand(req);
}

void AudioController::resumeNow() {
  Serial.println(F("AudioController: resume"));
  _mp3.start();
}

void AudioController::stop() {
  AudioCommandRequest req;
  req.command = AudioCommand::STOP;
  enqueueCommand(req);
}

void AudioController::stopNow() {
  Serial.println(F("AudioController: stop"));
  _mp3.stop();
}

void AudioController::startOver() {
  AudioCommandRequest req;
  req.command = AudioCommand::START_OVER;
  enqueueCommand(req);
}

void AudioController::startOverNow() {
  Serial.println(F("AudioController: start over"));
  playTrackNow(_currentTrack);
}

// Legacy name, kept for backward compatibility with existing callers.
void AudioController::playFile(const int fileNum) {
  playTrack(fileNum);
}

// ============================================================================
// Technical helpers -- DFPlayer/hardware details, no business meaning.
// ============================================================================

// Sets the working volume and waits for the clone chip's command registry
// to settle. Only needed before commands that start fresh playback
// (playMp3FolderTrack) -- pause/resume/stop are simple commands to an
// already-initialized chip and don't need this.
void AudioController::primeDfPlayer() {
  Serial.println(F("Connecting to DFPlayer..."));
  _mp3.setVolume(DEFAULT_VOLUME);
  vTaskDelay(pdMS_TO_TICKS(VOLUME_SETTLE_MS));
}


void AudioController::signalPlaybackStarted() {
}