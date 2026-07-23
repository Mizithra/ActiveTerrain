#pragma once
#include <Arduino.h>

// Topics these callbacks respond to. Populated by setupCallbacks() from
// the objective's base topic, since they share a prefix with the RFID
// topic defined in main.ino.
extern String LED_TOPIC;
extern String OLED_TOPIC;
extern String AUDIO_TOPIC;

// Call once from setup(), BEFORE registering these handlers with
// MqttHandler -- this is what populates the topic strings above and
// initializes any hardware pins these handlers need (e.g. the LED pin).
void setupCallbacks(const String &objectiveTopic);

// Event handlers -- one per topic. Each function is responsible for
// parsing its own JSON payload shape; they know nothing about MQTT itself,
// just "a message arrived, here's the topic and raw payload string."
void handle_led_event(const String &topic, const String &payload);
void handle_oled_event(const String &topic, const String &payload);
void handle_audio_event(const String &topic, const String &payload);
