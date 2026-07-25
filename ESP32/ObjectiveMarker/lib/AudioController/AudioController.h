#pragma once
#include <Arduino.h>

// Stub -- logs what it WOULD play. Wire in real playback (e.g. DFPlayer
// Mini over serial) once hardware is connected.
class AudioController {
public:
  void begin(const String &objectiveTopic);
  void handleMqttEvent(const String &topic, const String &payload);

  const String &topic() const { return _topic; }

private:
  String _topic;
};
