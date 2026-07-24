#pragma once
#include <Arduino.h>
#include <Adafruit_PN532.h>
#include "MqttRouter.h"
#include "LedController.h"
#include "OledController.h"
#include "AudioController.h"
#include "RfidTracker.h"
#include "RegistrationController.h"

// Owns every subsystem for one objective marker and wires them together.
// The only class main .ino talks to.
class ObjectiveNode {
public:
  ObjectiveNode(const String &objectiveTopic, uint8_t ledPin, uint8_t sdaPin, uint8_t sclPin);

  void begin(const char *wifiSsid, const char *wifiPassword,
             const char *mqttBroker, int mqttPort,
             const char *mqttUsername, const char *mqttPassword);
  void loop();

private:
  String _objectiveTopic;
  Adafruit_PN532 _nfc;
  MqttRouter _mqtt;
  LedController _led;
  OledController _oled;
  AudioController _audio;
  RfidTracker _rfid;
  RegistrationController _registration;

  void connectWifi(const char *ssid, const char *password);
};
