#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <Wire.h>
#include <Adafruit_PN532.h>
#include <ArduinoJson.h>

#include "secrets.h"

const char *topic = "battlefield/rfid";

const int mqtt_port = 8883;


#define SDA_PIN 21
#define SCL_PIN 22

#define LED_PIN 2

#define RFID_TIMEOUT 50
#define DEBOUNCE_MS 5000
#define MAX_TRACKED_CARDS 10

#define HEARTBEAT_INTERVAL_MS 1000  // publish once per second while card is present

unsigned long lastHeartbeat = 0;

Adafruit_PN532 nfc(SDA_PIN, SCL_PIN);
WiFiClientSecure espClient;
PubSubClient client(espClient);

unsigned long lastReconnectAttempt = 0;

// --- Card history tracking ---
struct CardRecord {
  char uid[15];         // hex string, e.g. "04A3B2C1" + null
  unsigned long lastSeen;
  bool used;
};
CardRecord cardHistory[MAX_TRACKED_CARDS];

void uidToString(uint8_t *uid, uint8_t uidLength, char *out) {
  char *p = out;
  for (uint8_t i = 0; i < uidLength; i++) {
    p += sprintf(p, "%02X", uid[i]);
  }
  *p = '\0';
}


void callback(char *topic, byte *payload, unsigned int length) {
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message: ");
  for (int i = 0; i < length; i++) Serial.print((char)payload[i]);
  Serial.println();
}

void setup_led()
{
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
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
    client.subscribe(topic);
    return true;
  } else {
    Serial.print("failed, state ");
    Serial.println(client.state());
    return false;
  }
}



String createRFIDPayload(String uid) {
  StaticJsonDocument<128> doc;

  doc["timestamp"] = millis();  // simple device uptime timestamp
  doc["uid"] = uid;

  String output;
  serializeJson(doc, output);
  return output;
}

void nfc_func() {
  uint8_t success;
  uint8_t uid[7];
  uint8_t uidLength;

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, RFID_TIMEOUT);

  if (success) {
    unsigned long now = millis();
    if (now - lastHeartbeat >= HEARTBEAT_INTERVAL_MS) {
      lastHeartbeat = now;
      char uidStr[15];
      uidToString(uid, uidLength, uidStr);
      if (client.connected()) {
        String payload = createRFIDPayload(uidStr);
        client.publish(topic, payload.c_str());      }
    }
  }
  // no "else" needed — if nothing's detected, we simply stop heartbeating,
  // and Python's check_departures() notices the silence
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

  nfc_func();
}