#pragma once
#include <Arduino.h>

// A handler for one topic. Receives the topic (in case one function is ever
// reused for more than one) and the raw payload string -- each handler is
// responsible for parsing its own JSON shape.
typedef void (*TopicHandler)(const String &topic, const String &payload);

namespace MqttHandler {

  // Call once from setup(), after WiFi is connected. Configures the
  // connection but does not connect yet -- that happens inside loop().
  void begin(const char *broker, int port, const char *username, const char *password);

  // Register a handler for a topic. Call these in setup(), before the
  // first successful connect, so the initial subscribe picks them all up.
  void registerTopicHandler(const String &topic, TopicHandler handler);

  // Call every loop() iteration. Handles reconnect attempts (throttled
  // internally) and services incoming messages via the registered handlers.
  void loop();

  bool isConnected();

  // Returns false if not connected or if the underlying publish failed.
  bool publish(const String &topic, const String &payload);

  // Services the underlying MQTT client (keepalive ping, incoming message
  // processing) WITHOUT attempting reconnects. Intended to be called
  // periodically from inside a long blocking handler (like registration
  // mode) so the connection doesn't time out while you wait on hardware.
  void pump();

}