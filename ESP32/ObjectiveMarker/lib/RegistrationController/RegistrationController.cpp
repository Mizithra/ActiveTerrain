#include "RegistrationController.h"
#include <ArduinoJson.h>

RegistrationController::RegistrationController(Adafruit_PN532 &nfc, MqttRouter &mqtt, LedController &led)
  : _nfc(nfc), _mqtt(mqtt), _led(led), _cancelRequested(false) {}

void RegistrationController::begin(const String &objectiveTopic) {
  String base_registration_topic = "battlefield/terrain/registration";
  _startTopic = base_registration_topic + "/register_start";
  _resultTopic = base_registration_topic + "/register_result";
  _endTopic = base_registration_topic + "/register_end";
}

void RegistrationController::handleStart(const String &topic, const String &payload) {
  Serial.println("RegistrationController: entering blocking scan");
  _cancelRequested = false;
  _led.ledOn();

  uint8_t uid[7], uidLength = 0, success = 0;
  unsigned long start = millis(), lastPump = start;

  while (!success && !_cancelRequested && (millis() - start) < TIMEOUT_MS) {
    success = _nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, POLL_MS);
    if (millis() - lastPump > PUMP_INTERVAL_MS) {
      _mqtt.pump();  // keep the connection alive during this blocking wait
      lastPump = millis();
    }
  }

  _led.ledOff();

  if (_cancelRequested) {
    Serial.println("RegistrationController: registration cancelled");
    return;
  }

  JsonDocument doc;
  if (success) {
    char uidStr[15];
    char *p = uidStr;
    for (uint8_t i = 0; i < uidLength; i++) p += sprintf(p, "%02X", uid[i]);
    *p = '\0';
    doc["uid"] = uidStr;
    Serial.printf("RegistrationController: scanned %s\n", uidStr);
  } else {
    doc["uid"] = nullptr;
    doc["error"] = "timeout";
    Serial.println("RegistrationController: timed out");
  }

  String out;
  serializeJson(doc, out);
  _mqtt.publish(_resultTopic, out);
}

void RegistrationController::handleEnd(const String &topic, const String &payload) {
  Serial.println("RegistrationController: end message received, cancelling scan and turning off LED");
  _cancelRequested = true;
  _led.ledOff();
}
