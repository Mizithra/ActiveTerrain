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
  constexpr uint32_t TRACK_COMMAND_SETTLE_MS = 500; // settle time after issuing a play command

  constexpr uint8_t  BUZZER_PIN            = 26;
  constexpr uint8_t  BUZZER_BEEP_COUNT     = 3;
  constexpr uint32_t BUZZER_BEEP_MS        = 1000;
}


// Target Serial2 globally to align with Pins 16 & 17
AudioController::AudioController()
  : _serial(2), _mp3(_serial) {}   // UART2, matches your FPS_RX/FPS_TX pins

void AudioController::begin(const String &objectiveTopic) {
  _topic = objectiveTopic + "/audio_control";

  _mp3.begin();
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
  executeCommand(req);
}

// The only place that knows the enum-to-method mapping.
void AudioController::executeCommand(const AudioCommandRequest &req) {
  switch (req.command) {
    case AudioCommand::PLAY_TRACK: playTrack(req.track); break;
    case AudioCommand::PLAY_NEXT:  playNext(); break;
    case AudioCommand::PLAY_PREV:  playPrev(); break;
    case AudioCommand::PAUSE:      pause(); break;
    case AudioCommand::RESUME:     resume(); break;
    case AudioCommand::STOP:       stop(); break;
    case AudioCommand::START_OVER: startOver(); break;
    case AudioCommand::UNKNOWN:
    default:
      Serial.println(F("AudioController: unrecognized command, ignoring"));
      break;
  }
}

// ============================================================================
// Playback control API -- one function per command.
// ============================================================================

void AudioController::playTrack(int track) {
  primeDfPlayer();

  Serial.printf("AudioController: playing track %d\n", track);
  _mp3.playMp3FolderTrack(track);
  // delay(TRACK_COMMAND_SETTLE_MS); // final delay step to protect transmission cycle

  _currentTrack = track;
  signalPlaybackStarted();
}

void AudioController::playNext() {
  playTrack(_currentTrack + 1);
}

void AudioController::playPrev() {
  playTrack(_currentTrack - 1);
}

void AudioController::pause() {
  Serial.println(F("AudioController: pause"));
  _mp3.pause();
}

void AudioController::resume() {
  Serial.println(F("AudioController: resume"));
  _mp3.start();
}

void AudioController::stop() {
  Serial.println(F("AudioController: stop"));
  _mp3.stop();
}

void AudioController::startOver() {
  Serial.println(F("AudioController: start over"));
  playTrack(_currentTrack);
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
  delay(VOLUME_SETTLE_MS);
}


void AudioController::signalPlaybackStarted() {
  // pinMode(BUZZER_PIN, OUTPUT);
  // for (uint8_t i = 0; i < BUZZER_BEEP_COUNT; i++) {
  //   digitalWrite(BUZZER_PIN, HIGH);
  //   delay(BUZZER_BEEP_MS);
  //   digitalWrite(BUZZER_PIN, LOW);
  //   delay(BUZZER_BEEP_MS);
  // }
}