#pragma once
#include <Arduino.h>

// Topics these callbacks respond to. Populated by setupCallbacks() from
// the objective's base topic.
extern String LED_TOPIC;
extern String OLED_TOPIC;
extern String AUDIO_TOPIC;
extern String REGISTER_START_TOPIC;
extern String REGISTER_RESULT_TOPIC;

// Call once from setup(), BEFORE registering these handlers with
// MqttHandler -- this populates the topic strings above and initializes
// any hardware pins these handlers need (e.g. the LED pin).
void setupCallbacks(const String &objectiveTopic);

// Event handlers -- one per topic. Each function is responsible for
// parsing its own JSON payload shape; they know nothing about MQTT itself,
// just "a message arrived, here's the topic and raw payload string."
void handle_led_event(const String &topic, const String &payload);
void handle_oled_event(const String &topic, const String &payload);
void handle_audio_event(const String &topic, const String &payload);

// Registration mode: turns the LED on, BLOCKS until a tag is scanned (or
// times out), turns the LED off, then publishes the result. Intentionally
// blocking -- the LED itself is the "waiting for you" indicator, and this
// is a deliberate user-driven action (registering tags), not something
// that needs to happen in the background.
void handle_register_start_event(const String &topic, const String &payload);