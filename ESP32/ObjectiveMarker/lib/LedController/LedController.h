#pragma once
#include <Arduino.h>

// One LED pin. Drivable via MQTT (handleMqttEvent) or triggered directly
// for local, immediate feedback (ledOn/ledOff) -- e.g. departure
// detection that shouldn't wait on a round trip to the backend.
class LedController {
public:
  explicit LedController(uint8_t pin) : _pin(pin) {}

  void begin(const String &objectiveTopic);
  void ledOn();
  void ledOff();
  void handleMqttEvent(const String &topic, const String &payload);

  const String &topic() const { return _topic; }

private:
  uint8_t _pin;
  String _topic;
};
