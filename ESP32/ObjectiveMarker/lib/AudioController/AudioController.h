#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include "HardwareSerial.h"
#include <DFMiniMp3.h>

// Implement the mandatory Makuna notification class with modern method signatures
class Mp3Notify {
public:
  static void PrintlnSourceAction(DFMiniMp3<HardwareSerial, Mp3Notify>& mp3, DfMp3_PlaySources source, const char* action) {
    Serial.print("Source Action, ");
    Serial.print(source);
    Serial.print(" ");
    Serial.println(action);
  }
  
  static void OnError(DFMiniMp3<HardwareSerial, Mp3Notify>& mp3, uint16_t errorCode) {
    Serial.print("Comms Error: ");
    Serial.println(errorCode);
  }
  
  static void OnPlayFinished(DFMiniMp3<HardwareSerial, Mp3Notify>& mp3, DfMp3_PlaySources source, uint16_t track) {
    Serial.print("Finished track: ");
    Serial.println(track);
  }
  
  static void OnPlaySourceOnline(DFMiniMp3<HardwareSerial, Mp3Notify>& mp3, DfMp3_PlaySources source) {}
  static void OnPlaySourceInserted(DFMiniMp3<HardwareSerial, Mp3Notify>& mp3, DfMp3_PlaySources source) {}
  static void OnPlaySourceRemoved(DFMiniMp3<HardwareSerial, Mp3Notify>& mp3, DfMp3_PlaySources source) {}
};

// Playback commands available via the control API / MQTT.
enum class AudioCommand {
    PLAY_TRACK,   // play a specific track number (from the mp3 folder)
    PLAY_NEXT,    // play (current track + 1)
    PLAY_PREV,    // play (current track + 1)
    PAUSE,        // pause playback, resumable
    RESUME,       // continue playback from pause
    STOP,         // stop playback outright
    START_OVER,   // replay the current track from the beginning
    UNKNOWN       // payload didn't map to a recognized command
};

// Fixed-size-ish request describing one playback command. Mirrors the
// OledController pattern: this struct is what the "business logic" layer
// (MQTT parsing) hands to the "technical" layer (actual DFPlayer calls).
struct AudioCommandRequest {
    AudioCommand command = AudioCommand::UNKNOWN;
    int track = 0; // only meaningful for PLAY_TRACK; ignored otherwise
};

// Drives a DFPlayer Mini over UART2 via the Makuna DFMiniMp3 library.
class AudioController {
public:
  AudioController();

  void begin(const String &objectiveTopic);
  void handleMqttEvent(const String &topic, const String &payload);

  // --- playback control API ----------------------------------------------
  void playTrack(int track);   // play a specific track from the mp3 folder
  void playNext();              // play (current track + 1)
  void playPrev();              // play (current track - 1)
  void pause();                 // pause, resumable
  void resume();                 // continue from pause
  void stop();                   // stop outright
  void startOver();              // replay the current track from the start

  // Legacy name, kept for backward compatibility -- delegates to playTrack().
  void playFile(const int fileNum);

  const String &topic() const { return _topic; }

private:
  String _topic;
  HardwareSerial _serial;   // owned here, must be declared before _mp3
  DFMiniMp3<HardwareSerial, Mp3Notify> _mp3;

  int _currentTrack = 1; // last track played via playTrack()/playNext()/startOver()

  // ---- MQTT / business logic ---------------------------------------------
  // Interprets an incoming MQTT payload (JSON {"command","track"}, or a
  // bare numeric string as a "play this track" fallback) into a command
  // request. Knows nothing about the DFPlayer itself.
  AudioCommandRequest parseMqttPayload(const String &payload);
  static AudioCommand commandFromString(const String &name);
  void executeCommand(const AudioCommandRequest &req); // dispatches to the control API above

  // ---- technical helpers ---------------------------------------------
  void primeDfPlayer();          // volume + settle delay before a playMp3FolderTrack command
  void signalPlaybackStarted();  // buzzer confirmation chirp
};