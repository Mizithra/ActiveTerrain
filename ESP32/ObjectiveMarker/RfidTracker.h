#pragma once
#include <Arduino.h>
#include <functional>
#include <Adafruit_PN532.h>
#include "MqttRouter.h"

// Tracks which RFID tags are currently on this objective. Reading and
// publishing stay separate on purpose: poll() runs every loop for
// frequent detection, publishActive() independently decides what (if
// anything) needs to go out over MQTT right now.
class RfidTracker {
public:
  static const int MAX_TAGS = 10;

  RfidTracker(Adafruit_PN532 &nfc, MqttRouter &mqtt);

  void begin(const String &objectiveTopic);
  void poll();            // read the antenna, update timestamps
  void publishActive();   // expire stale tags, publish due heartbeats

  // Fires exactly once, the moment the tracker goes from "something
  // present" to "nothing present" -- e.g. wire to LedController::turnOff.
  void onAllTagsExpired(std::function<void()> callback) { _onAllTagsExpired = callback; }

private:
  struct CardRecord {
    char uid[15] = {0};
    unsigned long lastPolled = 0;
    unsigned long lastPublished = 0;
    bool active = false;
  };

  static constexpr unsigned long PRESENCE_WINDOW_MS = 2000;
  static constexpr unsigned long HEARTBEAT_INTERVAL_MS = 1000;
  static constexpr unsigned long POLL_TIMEOUT_MS = 30;

  Adafruit_PN532 &_nfc;
  MqttRouter &_mqtt;
  String _topic;
  CardRecord _cards[MAX_TAGS];
  bool _anyWasActive = false;
  std::function<void()> _onAllTagsExpired;

  CardRecord *findOrCreate(const char *uid);
  static void uidToString(uint8_t *uid, uint8_t len, char *out);
  String makePayload(const char *uid) const;
};
