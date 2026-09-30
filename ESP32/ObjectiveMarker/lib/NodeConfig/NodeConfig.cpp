#include "NodeConfig.h"
#include <SD.h>
#include <SPI.h>
#include <ArduinoJson.h>

#define SD_CS 5

bool loadNodeConfig(NodeConfig &cfg) {
  Serial.println("Reading SD Card Config");
  if (!SD.begin(SD_CS))
  {
    Serial.println("Config: SD mount failed");
    return false;
    }
  File f = SD.open("/config.json", FILE_READ);
  if (!f){
    Serial.println("Config: /config.json missing");
    SD.end();
    return false;
    }
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, f);
  f.close();
  SD.end();
  if (err) { Serial.printf("Config: bad JSON (%s)\n", err.c_str()); return false; }

  cfg.topic = doc["mqtt_topic"] | "";
  cfg.topic.trim();
  if (cfg.topic.isEmpty()) {
        Serial.println("Config: mqtt_topic required");
        return false;
    }
  cfg.name = doc["name"] | cfg.topic.c_str();
  cfg.registrationEnabled = doc["registration_enabled"] | false;
  cfg.presenceWindowMs = doc["presence_window_ms"] | 2000;
  cfg.heartbeatMs = doc["heartbeat_ms"] | 1000;
  cfg.audioVolume = doc["audio_volume"] | 20;

  return true;
}