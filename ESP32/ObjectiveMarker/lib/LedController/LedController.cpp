#include "LedController.h"
#include <ArduinoJson.h>

void LedController::begin(const String &objectiveTopic) {
  _topic = objectiveTopic + "/led_control";
  pinMode(_pin, OUTPUT);
  ledOff();
}

void LedController::ledOn() {
  digitalWrite(_pin, HIGH);
}

void LedController::ledOff() {
  digitalWrite(_pin, LOW);
}

void LedController::handleMqttEvent(const String &topic, const String &payload) {
  JsonDocument doc;
  if (deserializeJson(doc, payload)) {
    Serial.println("LedController: failed to parse JSON payload");
    return;
  }
  const char *state = doc["state"] | "off";
  strcmp(state, "on") == 0 ? ledOn() : ledOff();
  Serial.printf("LedController: set to '%s'\n", state);
  // doc["color"] / doc["pattern"] arrive too -- wire in once on
  // addressable LEDs (e.g. NeoPixel) instead of a single-color pin.
}
