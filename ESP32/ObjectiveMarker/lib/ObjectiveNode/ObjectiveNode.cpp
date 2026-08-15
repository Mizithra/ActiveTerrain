#include "ObjectiveNode.h"
#include <WiFi.h>

ObjectiveNode::ObjectiveNode(const String &objectiveTopic, uint8_t ledPin, uint8_t sdaPin, uint8_t sclPin)
  : _objectiveTopic(objectiveTopic),
    _nfc(sdaPin, sclPin),
    _led(ledPin),
    _rfid(_nfc, _mqtt),
    _registration(_nfc, _mqtt, _led) {}

void ObjectiveNode::connectWifi(const char *ssid, const char *password) {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("WiFi connected");
}

void ObjectiveNode::begin(const char *wifiSsid, const char *wifiPassword,
                           const char *mqttBroker, int mqttPort,
                           const char *mqttUsername, const char *mqttPassword) {
  connectWifi(wifiSsid, wifiPassword);

  _led.begin(_objectiveTopic);
  _oled.begin(_objectiveTopic);
  _audio.begin(_objectiveTopic);
  _rfid.begin(_objectiveTopic);
  _registration.begin(_objectiveTopic);

  // Local, immediate reaction -- doesn't wait on a backend round trip.
  _rfid.onAllTagsExpired([this]() { _led.ledOff(); });

  _mqtt.begin(mqttBroker, mqttPort, mqttUsername, mqttPassword);
  _mqtt.registerHandler(_led.topic(), [this](const String &t, const String &p) { _led.handleMqttEvent(t, p); });
  _mqtt.registerHandler(_oled.topic(), [this](const String &t, const String &p) { _oled.handleMqttEvent(t, p); });
  _mqtt.registerHandler(_audio.topic(), [this](const String &t, const String &p) { _audio.handleMqttEvent(t, p); });
  _mqtt.registerHandler(_registration.startTopic(), [this](const String &t, const String &p) { _registration.handleStart(t, p); });
  _mqtt.registerHandler(_registration.endTopic(), [this](const String &t, const String &p) { _registration.handleEnd(t, p); });

  if (!_nfc.begin()) {
    Serial.println("Didn't find PN532 board");
    while (1);
  }
  if (!_nfc.getFirmwareVersion()) {
    Serial.println("Didn't get PN532 firmware version");
    while (1);
  }
  _nfc.SAMConfig();
  Serial.println("PN532 initialized");
  _oled.run(32, 33, 0x3C);  // SDA, SCL, I2C address
  
}

void ObjectiveNode::loop() {
  _mqtt.loop();
  _rfid.poll();
  _rfid.publishActive();
}
