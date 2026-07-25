#include <Arduino.h>
#include "secrets.h"
#include "ObjectiveNode.h"

#define OBJECTIVE_TOPIC "battlefield/terrain/home_base"
#define LED_PIN 2
#define SDA_PIN 21
#define SCL_PIN 22
#define MQTT_PORT 8883

ObjectiveNode node(OBJECTIVE_TOPIC, LED_PIN, SDA_PIN, SCL_PIN);

void setup() {
  Serial.begin(115200);
  node.begin(WIFI_SSID, WIFI_PASSWORD, MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD);
}

void loop() {
  node.loop();
}
