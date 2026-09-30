// NodeConfig.h
#pragma once

#include <Arduino.h>
struct NodeConfig {
  String name, topic;
  bool registrationEnabled = false;
  uint32_t presenceWindowMs = 2000, heartbeatMs = 1000;
  uint8_t audioVolume = 20;
};
bool loadNodeConfig(NodeConfig &cfg);