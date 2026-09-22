#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
// Stub -- logs what it WOULD display. Wire in real display calls once
// hardware is connected.
class OledController {
private:
public:
  OledController();
  ~OledController();
  void begin(const String &objectiveTopic);
  void handleMqttEvent(const String &topic, const String &payload);
  bool writeText(String payload);

  const String &topic() const { return _topic; }

private:
  String _topic;

  TwoWire i2c_oled;
  Adafruit_SSD1306* display;
};
