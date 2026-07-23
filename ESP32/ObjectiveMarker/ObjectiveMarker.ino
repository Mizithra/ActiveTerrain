#include <Arduino.h>
#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_PN532.h>
#include <ArduinoJson.h>
#include "secrets.h"
#include "MqttHandler.h"
#include "Callbacks.h"

// --- Per-objective identity -------------------------------------------
#define OBJECTIVE_TOPIC "battlefield/terrain/home_base"
String RFID_TOPIC;

const int mqtt_port = 8883;
#define SDA_PIN 21
#define SCL_PIN 22
#define POLL_TIMEOUT_MS 30

#define MAX_TRACKED_CARDS 10
#define PRESENCE_WINDOW_MS 2000
#define PER_UID_HEARTBEAT_MS 1000

Adafruit_PN532 nfc(SDA_PIN, SCL_PIN);

struct CardRecord {
  char uid[15];
  unsigned long lastPolled;
  unsigned long lastPublished;
  bool active;
};
CardRecord cardHistory[MAX_TRACKED_CARDS];

void uidToString(uint8_t *uid, uint8_t uidLength, char *out) {
  char *p = out;
  for (uint8_t i = 0; i < uidLength; i++) {
    p += sprintf(p, "%02X", uid[i]);
  }
  *p = '\0';
}

CardRecord *findOrCreateRecord(const char *uid) {
  for (int i = 0; i < MAX_TRACKED_CARDS; i++) {
    if (cardHistory[i].active && strcmp(cardHistory[i].uid, uid) == 0) {
      return &cardHistory[i];
    }
  }
  for (int i = 0; i < MAX_TRACKED_CARDS; i++) {
    if (!cardHistory[i].active) {
      cardHistory[i].active = true;
      strncpy(cardHistory[i].uid, uid, sizeof(cardHistory[i].uid) - 1);
      cardHistory[i].uid[sizeof(cardHistory[i].uid) - 1] = '\0';
      cardHistory[i].lastPublished = 0;
      return &cardHistory[i];
    }
  }
  int oldestIdx = 0;
  unsigned long oldestTime = cardHistory[0].lastPolled;
  for (int i = 1; i < MAX_TRACKED_CARDS; i++) {
    if (cardHistory[i].lastPolled < oldestTime) {
      oldestTime = cardHistory[i].lastPolled;
      oldestIdx = i;
    }
  }
  strncpy(cardHistory[oldestIdx].uid, uid, sizeof(cardHistory[oldestIdx].uid) - 1);
  cardHistory[oldestIdx].uid[sizeof(cardHistory[oldestIdx].uid) - 1] = '\0';
  cardHistory[oldestIdx].lastPublished = 0;
  return &cardHistory[oldestIdx];
}

String createRFIDPayload(const char *uid) {
  StaticJsonDocument<128> doc;
  doc["timestamp"] = millis();
  doc["uid"] = uid;
  String output;
  serializeJson(doc, output);
  return output;
}

void poll_rfid() {
  uint8_t uid[7];
  uint8_t uidLength;

  uint8_t success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, POLL_TIMEOUT_MS);
  if (!success) {
    return;
  }

  char uidStr[15];
  uidToString(uid, uidLength, uidStr);

  CardRecord *rec = findOrCreateRecord(uidStr);
  rec->lastPolled = millis();
  Serial.printf("Polled tag: %s\n", uidStr);
}

void publish_active_cards() {
  unsigned long now = millis();

  for (int i = 0; i < MAX_TRACKED_CARDS; i++) {
    if (!cardHistory[i].active) continue;

    bool stillPresent = (now - cardHistory[i].lastPolled) <= PRESENCE_WINDOW_MS;
    if (!stillPresent) {
      Serial.printf("Tag expired (no reads in %dms): %s\n", PRESENCE_WINDOW_MS, cardHistory[i].uid);
      cardHistory[i].active = false;
      continue;
    }

    bool dueForHeartbeat = (now - cardHistory[i].lastPublished) >= PER_UID_HEARTBEAT_MS;
    if (!dueForHeartbeat) continue;

    if (!MqttHandler::isConnected()) {
      Serial.printf("Skipping publish for %s: MQTT not connected\n", cardHistory[i].uid);
      continue;
    }

    cardHistory[i].lastPublished = now;
    String payload = createRFIDPayload(cardHistory[i].uid);
    bool ok = MqttHandler::publish(RFID_TOPIC, payload);
    Serial.printf("Published %s: %s (%s)\n", cardHistory[i].uid, payload.c_str(), ok ? "ok" : "FAILED");
  }
}

// ===========================================================================

void setup() {
  Serial.begin(115200);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("WiFi Connected");

  RFID_TOPIC = String(OBJECTIVE_TOPIC) + "/rfid_scan";

  // Callbacks module sets up its own topics + hardware (e.g. LED pin) first
  setupCallbacks(OBJECTIVE_TOPIC);

  //  MqttHandler is configured and told which topics map to which
  // callback functions. This is the one place both modules are visible
  // to each other.
  MqttHandler::begin(MQTT_BROKER, mqtt_port, MQTT_USERNAME, MQTT_PASSWORD);
  MqttHandler::registerTopicHandler(LED_TOPIC, handle_led_event);
  MqttHandler::registerTopicHandler(OLED_TOPIC, handle_oled_event);
  MqttHandler::registerTopicHandler(AUDIO_TOPIC, handle_audio_event);

  if (!nfc.begin()) {
    Serial.println("Didn't find PN532 board");
    while (1);
  }
  uint32_t version = nfc.getFirmwareVersion();
  if (!version) {
    Serial.println("Didn't get PN532 firmware version");
    while (1);
  }
  nfc.SAMConfig();
  Serial.println("PN532 initialized!");
}

void loop() {
  MqttHandler::loop();
  poll_rfid();
  publish_active_cards();
}
