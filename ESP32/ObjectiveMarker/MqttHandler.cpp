#include "MqttHandler.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

namespace {

  WiFiClientSecure espClient;
  PubSubClient client(espClient);

  #define MAX_TOPIC_ROUTES 10
  struct TopicRoute {
    String topic;
    TopicHandler handler;
  };
  TopicRoute topicRoutes[MAX_TOPIC_ROUTES];
  int topicRouteCount = 0;

  unsigned long lastReconnectAttempt = 0;
  const char *storedUsername = nullptr;
  const char *storedPassword = nullptr;

  void subscribeAllRegisteredTopics() {
    for (int i = 0; i < topicRouteCount; i++) {
      client.subscribe(topicRoutes[i].topic.c_str());
      Serial.printf("MqttHandler: subscribed to %s\n", topicRoutes[i].topic.c_str());
    }
  }

  void mqttCallback(char *topicReceived, byte *payload, unsigned int length) {
    String topic = String(topicReceived);
    String message;
    message.reserve(length);
    for (unsigned int i = 0; i < length; i++) message += (char)payload[i];

    Serial.printf("MqttHandler: message on %s: %s\n", topic.c_str(), message.c_str());

    for (int i = 0; i < topicRouteCount; i++) {
      if (topicRoutes[i].topic == topic) {
        topicRoutes[i].handler(topic, message);
        return;
      }
    }
    Serial.printf("MqttHandler: no handler registered for topic: %s\n", topic.c_str());
  }

  bool attemptReconnect() {
    String client_id = "esp32-client-" + String(WiFi.macAddress());
    Serial.printf("MqttHandler: connecting as %s...\n", client_id.c_str());
    if (client.connect(client_id.c_str(), storedUsername, storedPassword)) {
      Serial.println("MqttHandler: connected");
      subscribeAllRegisteredTopics();
      return true;
    } else {
      Serial.print("MqttHandler: connect failed, state ");
      Serial.println(client.state());
      return false;
    }
  }

}  // anonymous namespace

namespace MqttHandler {

  void begin(const char *broker, int port, const char *username, const char *password) {
    storedUsername = username;
    storedPassword = password;
    espClient.setInsecure();
    client.setServer(broker, port);
    client.setCallback(mqttCallback);
  }

  void registerTopicHandler(const String &topic, TopicHandler handler) {
    if (topicRouteCount >= MAX_TOPIC_ROUTES) {
      Serial.println("MqttHandler: MAX_TOPIC_ROUTES exceeded, dropping registration");
      return;
    }
    topicRoutes[topicRouteCount].topic = topic;
    topicRoutes[topicRouteCount].handler = handler;
    topicRouteCount++;
  }

  void loop() {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("MqttHandler: WiFi lost, skipping this cycle");
      return;
    }

    if (!client.connected()) {
      unsigned long now = millis();
      if (now - lastReconnectAttempt > 2000) {
        lastReconnectAttempt = now;
        attemptReconnect();
      }
    } else {
      client.loop();
    }
  }

  bool isConnected() {
    return client.connected();
  }

  bool publish(const String &topic, const String &payload) {
    if (!client.connected()) return false;
    return client.publish(topic.c_str(), payload.c_str());
  }

  void pump() {
    if (client.connected()) {
      client.loop();
    }
  }

}