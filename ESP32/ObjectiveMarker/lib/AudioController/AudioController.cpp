#include "AudioController.h"
#include <ArduinoJson.h>

void AudioController::begin(const String &objectiveTopic) {
  _topic = objectiveTopic + "/audio_control";
}

void AudioController::handleMqttEvent(const String &topic, const String &payload) {
  JsonDocument doc;
  if (deserializeJson(doc, payload)) {
    Serial.println("AudioController: failed to parse JSON payload");
    return;
  }
  const char *soundFile = doc["sound_file"] | "";
  Serial.printf("AudioController: would play '%s'\n", soundFile);
  // TODO: myDFPlayer.playMp3Folder(...);
}
