#include "Callbacks.h"
#include <ArduinoJson.h>

#define LED_PIN 2

String LED_TOPIC;
String OLED_TOPIC;
String AUDIO_TOPIC;

void setupCallbacks(const String &objectiveTopic) {
  LED_TOPIC = objectiveTopic + "/led_control";
  OLED_TOPIC = objectiveTopic + "/oled_control";
  AUDIO_TOPIC = objectiveTopic + "/audio_control";

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);  // start OFF; backend turns it on when a unit arrives
}

void handle_led_event(const String &topic, const String &payload) {
  StaticJsonDocument<128> doc;
  if (deserializeJson(doc, payload)) {
    Serial.println("handle_led_event: failed to parse JSON payload");
    return;
  }
  const char *state = doc["state"] | "off";
  digitalWrite(LED_PIN, strcmp(state, "on") == 0 ? HIGH : LOW);
  Serial.printf("handle_led_event: set to '%s'\n", state);

  // doc["color"] / doc["pattern"] are also sent by the backend based on
  // this objective's role. Wire those in once you're on addressable LEDs
  // (e.g. NeoPixel) rather than a single-color pin.
}

void handle_oled_event(const String &topic, const String &payload) {
  StaticJsonDocument<256> doc;
  if (deserializeJson(doc, payload)) {
    Serial.println("handle_oled_event: failed to parse JSON payload");
    return;
  }
  const char *text = doc["text"] | "";
  Serial.printf("handle_oled_event: would display '%s'\n", text);
  // TODO: wire in actual display calls once hardware is connected, e.g.
  //   display.clearDisplay();
  //   display.println(text);
  //   display.display();
}

void handle_audio_event(const String &topic, const String &payload) {
  StaticJsonDocument<128> doc;
  if (deserializeJson(doc, payload)) {
    Serial.println("handle_audio_event: failed to parse JSON payload");
    return;
  }
  const char *soundFile = doc["sound_file"] | "";
  Serial.printf("handle_audio_event: would play '%s'\n", soundFile);
  // TODO: wire in actual playback once hardware is connected, e.g. a
  // DFPlayer Mini over serial: myDFPlayer.playMp3Folder(...);
}
