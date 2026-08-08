#pragma once
#include <Arduino.h>

// Stub -- logs what it WOULD display. Wire in real display calls once
// hardware is connected.
class OledController {
public:
  void begin(const String &objectiveTopic);
  void handleMqttEvent(const String &topic, const String &payload);
  bool run(uint8_t sdaPin, uint8_t sclPin, uint8_t i2cAddress);

  const String &topic() const { return _topic; }

private:
  String _topic;
};
