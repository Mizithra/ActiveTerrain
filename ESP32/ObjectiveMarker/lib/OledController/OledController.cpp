#include "OledController.h"
#include <ArduinoJson.h>

void OledController::begin(const String &objectiveTopic) {
  _topic = objectiveTopic + "/oled_control";
}

void OledController::handleMqttEvent(const String &topic, const String &payload) {
  JsonDocument doc;
  if (deserializeJson(doc, payload)) {
    Serial.println("OledController: failed to parse JSON payload");
    return;
  }
  const char *text = doc["text"] | "";
  Serial.printf("OledController: would display '%s'\n", text);
  // TODO: display.clearDisplay(); display.println(text); display.display();
}
