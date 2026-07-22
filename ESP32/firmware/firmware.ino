#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <Wire.h>
#include <Adafruit_PN532.h>
#include <ArduinoJson.h>
#include "secrets.h"

// --- Per-objective identity -------------------------------------------
#define OBJECTIVE_TOPIC "battlefield/terrain/home_base"

const String RFID_TOPIC = String(OBJECTIVE_TOPIC) + "/rfid_scan";
const String LED_TOPIC  = String(OBJECTIVE_TOPIC) + "/led_control";

const int mqtt_port = 8883;
#define SDA_PIN 21
#define SCL_PIN 22
#define LED_PIN 2

// Kept short so polling is frequent -- with multiple tags on one objective,
// the antenna can only read one per poll, so fast, frequent polling is what
// lets it catch each tag often enough to be noticed as still present.
#define POLL_TIMEOUT_MS 30

#define MAX_TRACKED_CARDS 10
#define PRESENCE_WINDOW_MS 2000    // a tag not re-polled within this long is considered gone
#define PER_UID_HEARTBEAT_MS 1000  // don't publish the same uid more often than this

Adafruit_PN532 nfc(SDA_PIN, SCL_PIN);
WiFiClientSecure espClient;
PubSubClient client(espClient);

unsigned long lastReconnectAttempt = 0;

struct CardRecord {
  char uid[15];
  unsigned long lastPolled;     // last time the antenna actually read this uid
  unsigned long lastPublished;  // last time we sent an MQTT heartbeat for it
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

// Find an existing record for this uid, or claim a slot for a new one.
// If the table is full, evict whichever record was polled longest ago.
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

void callback(char *topicReceived, byte *payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) message += (char)payload[i];

  Serial.print("Message arrived on ");
  Serial.print(topicReceived);
  Serial.print(": ");
  Serial.println(message);

  if (String(topicReceived) == LED_TOPIC) {
    StaticJsonDocument<128> doc;
    if (deserializeJson(doc, message)) {
      Serial.println("Failed to parse LED command JSON");
      return;
    }
    const char *state = doc["state"] | "off";
    digitalWrite(LED_PIN, strcmp(state, "on") == 0 ? HIGH : LOW);
    Serial.printf("LED set to: %s\n", state);
  }
}

void setup_led() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
}

void setup() {
  Serial.begin(115200);
  setup_led();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("WiFi Connected");

  espClient.setInsecure();
  client.setServer(MQTT_BROKER, mqtt_port);
  client.setCallback(callback);

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

bool reconnectMQTT() {
  String client_id = "esp32-client-" + String(WiFi.macAddress());
  Serial.printf("Attempting MQTT connection as %s...\n", client_id.c_str());
  if (client.connect(client_id.c_str(), MQTT_USERNAME, MQTT_PASSWORD)) {
    Serial.println("MQTT connected");
    client.subscribe(LED_TOPIC.c_str());
    return true;
  } else {
    Serial.print("failed, state ");
    Serial.println(client.state());
    return false;
  }
}

// --- Reading -------------------------------------------------------------
// Does exactly one thing: poll the antenna, and if a tag is read, update
// its record's timestamp. No MQTT here at all -- this function has no idea
// whether anything ever gets published.
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

// --- Publishing ------------------------------------------------------------
// Decides, independently of reading, which currently-active tags need an
// MQTT heartbeat right now, and expires any that have gone quiet for too
// long. Safe to call every loop -- the per-uid throttle (lastPublished) and
// per-tag expiry (lastPolled) are both handled internally, so this doesn't
// spam MQTT even if called far more often than PER_UID_HEARTBEAT_MS.
void publish_active_cards() {
  unsigned long now = millis();

  for (int i = 0; i < MAX_TRACKED_CARDS; i++) {
    if (!cardHistory[i].active) continue;

    bool stillPresent = (now - cardHistory[i].lastPolled) <= PRESENCE_WINDOW_MS;
    if (!stillPresent) {
      Serial.printf("Tag expired (no reads in %dms): %s\n", PRESENCE_WINDOW_MS, cardHistory[i].uid);
      cardHistory[i].active = false;  // backend's own timeout handles the departure event
      continue;
    }

    bool dueForHeartbeat = (now - cardHistory[i].lastPublished) >= PER_UID_HEARTBEAT_MS;
    if (!dueForHeartbeat) continue;

    if (!client.connected()) {
      Serial.printf("Skipping publish for %s: MQTT not connected\n", cardHistory[i].uid);
      continue;
    }

    cardHistory[i].lastPublished = now;
    String payload = createRFIDPayload(cardHistory[i].uid);
    bool ok = client.publish(RFID_TOPIC.c_str(), payload.c_str());
    Serial.printf("Published %s: %s (%s)\n", cardHistory[i].uid, payload.c_str(), ok ? "ok" : "FAILED");
  }
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost, skipping MQTT this cycle");
  } else {
    if (!client.connected()) {
      unsigned long now = millis();
      if (now - lastReconnectAttempt > 2000) {
        lastReconnectAttempt = now;
        reconnectMQTT();
      }
    } else {
      client.loop();
    }
  }

  poll_rfid();            // read as often as possible
  publish_active_cards(); // decide what (if anything) to publish, separately
}