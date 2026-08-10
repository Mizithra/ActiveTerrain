#pragma once
#include <Arduino.h>



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

// Stub -- logs what it WOULD play. Wire in real playback (e.g. DFPlayer
// Mini over serial) once hardware is connected.
class AudioController {
public:
  void begin(const String &objectiveTopic);
  void handleMqttEvent(const String &topic, const String &payload);

  void testPlay(const String &fileName);
  const String &topic() const { return _topic; }

private:
  String _topic;

DFMiniMp3<HardwareSerial, Mp3Notify> mp3;


};
