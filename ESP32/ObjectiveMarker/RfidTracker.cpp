#include "RfidTracker.h"
#include <ArduinoJson.h>

RfidTracker::RfidTracker(Adafruit_PN532 &nfc, MqttRouter &mqtt) : _nfc(nfc), _mqtt(mqtt) {}

void RfidTracker::begin(const String &objectiveTopic) {
  _topic = objectiveTopic + "/rfid_scan";
}

void RfidTracker::uidToString(uint8_t *uid, uint8_t len, char *out) {
  char *p = out;
  for (uint8_t i = 0; i < len; i++) p += sprintf(p, "%02X", uid[i]);
  *p = '\0';
}

RfidTracker::CardRecord *RfidTracker::findOrCreate(const char *uid) {
  for (auto &c : _cards) {
    if (c.active && strcmp(c.uid, uid) == 0) return &c;
  }
  for (auto &c : _cards) {
    if (!c.active) {
      c.active = true;
      strncpy(c.uid, uid, sizeof(c.uid) - 1);
      c.lastPublished = 0;
      return &c;
    }
  }
  // table full -- evict whichever entry was polled longest ago
  CardRecord *oldest = &_cards[0];
  for (auto &c : _cards) if (c.lastPolled < oldest->lastPolled) oldest = &c;
  strncpy(oldest->uid, uid, sizeof(oldest->uid) - 1);
  oldest->lastPublished = 0;
  return oldest;
}

String RfidTracker::makePayload(const char *uid) const {
  StaticJsonDocument<128> doc;
  doc["timestamp"] = millis();
  doc["uid"] = uid;
  String out;
  serializeJson(doc, out);
  return out;
}

void RfidTracker::poll() {
  uint8_t uid[7], uidLength;
  if (!_nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, POLL_TIMEOUT_MS)) return;

  char uidStr[15];
  uidToString(uid, uidLength, uidStr);
  findOrCreate(uidStr)->lastPolled = millis();
  Serial.printf("RfidTracker: polled %s\n", uidStr);
}

void RfidTracker::publishActive() {
  unsigned long now = millis();
  bool anyActive = false;

  for (auto &c : _cards) {
    if (!c.active) continue;

    if (now - c.lastPolled > PRESENCE_WINDOW_MS) {
      Serial.printf("RfidTracker: %s expired\n", c.uid);
      c.active = false;
      continue;
    }
    anyActive = true;

    if (now - c.lastPublished < HEARTBEAT_INTERVAL_MS) continue;
    if (!_mqtt.isConnected()) {
      Serial.printf("RfidTracker: skipping %s, MQTT not connected\n", c.uid);
      continue;
    }
    c.lastPublished = now;
    String payload = makePayload(c.uid);
    bool ok = _mqtt.publish(_topic, payload);
    Serial.printf("RfidTracker: published %s (%s)\n", c.uid, ok ? "ok" : "FAILED");
  }

  // Fire the transition callback exactly once, not on every empty loop.
  if (_anyWasActive && !anyActive && _onAllTagsExpired) {
    _onAllTagsExpired();
  }
  _anyWasActive = anyActive;
}
