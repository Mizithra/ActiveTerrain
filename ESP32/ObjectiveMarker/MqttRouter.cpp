#include "MqttRouter.h"
#include <WiFi.h>

MqttRouter *MqttRouter::_instance = nullptr;

MqttRouter::MqttRouter() : _client(_espClient) {}

void MqttRouter::begin(const char *broker, int port, const char *username, const char *password) {
  _instance = this;
  _username = username;
  _password = password;
  _espClient.setInsecure();
  _client.setServer(broker, port);
  _client.setCallback(staticCallback);
}

void MqttRouter::registerHandler(const String &topic, TopicHandler handler) {
  if (_routeCount >= MAX_ROUTES) {
    Serial.println("MqttRouter: MAX_ROUTES exceeded, dropping registration");
    return;
  }
  _routes[_routeCount++] = {topic, handler};
}

void MqttRouter::loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("MqttRouter: WiFi lost, skipping this cycle");
    return;
  }
  if (!_client.connected()) {
    unsigned long now = millis();
    if (now - _lastReconnectAttempt > 2000) {
      _lastReconnectAttempt = now;
      reconnect();
    }
  } else {
    _client.loop();
  }
}

void MqttRouter::pump() {
  if (_client.connected()) _client.loop();
}

bool MqttRouter::isConnected() {
  return _client.connected();
}

bool MqttRouter::publish(const String &topic, const String &payload) {
  if (!_client.connected()) return false;
  return _client.publish(topic.c_str(), payload.c_str());
}

bool MqttRouter::reconnect() {
  String clientId = "esp32-client-" + String(WiFi.macAddress());
  Serial.printf("MqttRouter: connecting as %s...\n", clientId.c_str());
  if (_client.connect(clientId.c_str(), _username, _password)) {
    Serial.println("MqttRouter: connected");
    subscribeAll();
    return true;
  }
  Serial.printf("MqttRouter: connect failed, state %d\n", _client.state());
  return false;
}

void MqttRouter::subscribeAll() {
  for (int i = 0; i < _routeCount; i++) {
    _client.subscribe(_routes[i].topic.c_str());
    Serial.printf("MqttRouter: subscribed to %s\n", _routes[i].topic.c_str());
  }
}

void MqttRouter::handleMessage(char *topicReceived, byte *payload, unsigned int length) {
  String topic(topicReceived);
  String message;
  message.reserve(length);
  for (unsigned int i = 0; i < length; i++) message += (char)payload[i];
  Serial.printf("MqttRouter: message on %s: %s\n", topic.c_str(), message.c_str());

  for (int i = 0; i < _routeCount; i++) {
    if (_routes[i].topic == topic) {
      _routes[i].handler(topic, message);
      return;
    }
  }
  Serial.printf("MqttRouter: no handler for topic: %s\n", topic.c_str());
}

void MqttRouter::staticCallback(char *topic, byte *payload, unsigned int length) {
  if (_instance) _instance->handleMessage(topic, payload, length);
}
