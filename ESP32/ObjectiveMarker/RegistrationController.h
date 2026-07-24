#pragma once
#include <Arduino.h>
#include <Adafruit_PN532.h>
#include "MqttRouter.h"
#include "LedController.h"

// Blocking, user-driven tag enrollment: light on, wait for a scan (or
// time out), light off, publish the result. Blocking is intentional --
// the LED IS the "waiting for you" signal for a deliberate one-off
// action, not something that needs to run in the background.
class RegistrationController {
public:
  RegistrationController(Adafruit_PN532 &nfc, MqttRouter &mqtt, LedController &led);

  void begin(const String &objectiveTopic);
  void handleStart(const String &topic, const String &payload);

  const String &startTopic() const { return _startTopic; }

private:
  static constexpr unsigned long TIMEOUT_MS = 30000;
  static constexpr unsigned long POLL_MS = 100;
  static constexpr unsigned long PUMP_INTERVAL_MS = 1000;

  Adafruit_PN532 &_nfc;
  MqttRouter &_mqtt;
  LedController &_led;
  String _startTopic;
  String _resultTopic;
};
