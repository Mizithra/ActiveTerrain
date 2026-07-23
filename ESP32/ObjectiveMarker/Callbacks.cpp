#include "Callbacks.h"
#include "MqttHandler.h"
#include <ArduinoJson.h>
#include <Adafruit_PN532.h>

#define LED_PIN 2
#define REGISTRATION_TIMEOUT_MS 30000  // give up and report "no tag" after this long
#define REGISTRATION_POLL_MS 100       // how long each individual antenna poll waits
#define REGISTRATION_PUMP_INTERVAL_MS 1000  // how often to service MQTT during the wait

// Defined in main .ino -- declared here so this file can use the same
// physical reader for registration scans.
extern Adafruit_PN532 nfc;

String LED_TOPIC;
String OLED_TOPIC;
String AUDIO_TOPIC;
String REGISTER_START_TOPIC;
String REGISTER_RESULT_TOPIC;

void setupCallbacks(const String &objectiveTopic) {
  LED_TOPIC = objectiveTopic + "/led_control";
  OLED_TOPIC = objectiveTopic + "/oled_control";
  AUDIO_TOPIC = objectiveTopic + "/audio_control";
  REGISTER_START_TOPIC = "battlefield/terrain/register_start";
  REGISTER_RESULT_TOPIC = "battlefield/terrain/register_result";

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);  // start OFF; backend turns it on when needed
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
}

void handle_oled_event(const String &topic, const String &payload) {
  StaticJsonDocument<256> doc;
  if (deserializeJson(doc, payload)) {
    Serial.println("handle_oled_event: failed to parse JSON payload");
    return;
  }
  const char *text = doc["text"] | "";
  Serial.printf("handle_oled_event: would display '%s'\n", text);
}

void handle_audio_event(const String &topic, const String &payload) {
  StaticJsonDocument<128> doc;
  if (deserializeJson(doc, payload)) {
    Serial.println("handle_audio_event: failed to parse JSON payload");
    return;
  }
  const char *soundFile = doc["sound_file"] | "";
  Serial.printf("handle_audio_event: would play '%s'\n", soundFile);
}

void handle_register_start_event(const String &topic, const String &payload) {
  Serial.println("handle_register_start_event: entering registration scan (blocking)");
  digitalWrite(LED_PIN, HIGH);

  uint8_t uid[20];
  uint8_t uidLength = 0;
  uint8_t success = 0;
  unsigned long start = millis();
  unsigned long lastPump = start;

  while (!success && (millis() - start) < REGISTRATION_TIMEOUT_MS) {
    success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, REGISTRATION_POLL_MS);

    // Keep the MQTT connection alive during this wait. Without this, the
    // broker can drop the connection if the user takes a while to place a
    // tag, since PubSubClient's keepalive depends on client.loop() running
    // regularly -- and we're not returning to the main loop() during this
    // blocking wait.
    if (millis() - lastPump > REGISTRATION_PUMP_INTERVAL_MS) {
      MqttHandler::pump();
      lastPump = millis();
    }
  }

  digitalWrite(LED_PIN, LOW);

  StaticJsonDocument<128> doc;
  if (success) {
    char uidStr[15];
    char *p = uidStr;
    for (uint8_t i = 0; i < uidLength; i++) p += sprintf(p, "%02X", uid[i]);
    *p = '\0';
    doc["uid"] = uidStr;
    Serial.printf("handle_register_start_event: scanned %s\n", uidStr);
  } else {
    doc["uid"] = nullptr;
    doc["error"] = "timeout";
    Serial.println("handle_register_start_event: timed out waiting for a tag");
  }

  String out;
  serializeJson(doc, out);
  MqttHandler::publish(REGISTER_RESULT_TOPIC, out);
}