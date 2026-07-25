#pragma once
#include <Arduino.h>
#include <functional>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

// Owns the MQTT connection and routes incoming messages to registered
// handlers by topic. Handlers are std::function, so lambdas can capture
// `this` and call into other classes' member functions directly.
class MqttRouter {
public:
  using TopicHandler = std::function<void(const String &topic, const String &payload)>;

  MqttRouter();

  void begin(const char *broker, int port, const char *username, const char *password);
  void registerHandler(const String &topic, TopicHandler handler);
  void loop();   // call every Arduino loop(): reconnects + services messages
  void pump();   // services messages only, no reconnect -- for use inside blocking waits
  bool isConnected();
  bool publish(const String &topic, const String &payload);

private:
  static const int MAX_ROUTES = 10;
  struct Route { String topic; TopicHandler handler; };

  WiFiClientSecure _espClient;
  PubSubClient _client;
  Route _routes[MAX_ROUTES];
  int _routeCount = 0;
  unsigned long _lastReconnectAttempt = 0;
  const char *_username = nullptr;
  const char *_password = nullptr;

  bool reconnect();
  void subscribeAll();
  void handleMessage(char *topic, byte *payload, unsigned int length);

  // PubSubClient requires a plain C function pointer -- this is the one
  // unavoidable bit of indirection to bridge that into a member function.
  static MqttRouter *_instance;
  static void staticCallback(char *topic, byte *payload, unsigned int length);
};
