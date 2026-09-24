#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>

// Text animation effects available via showText().
enum class TextEffect {
    NONE,           // just draw it, centered, max size
    FLASH,          // blink on/off a few times, then stay lit
    TYPEWRITER,     // characters appear one at a time, left-to-right
    SLIDE_IN_LEFT,  // slides in from off-screen left to centered
    SLIDE_IN_RIGHT, // slides in from off-screen right to centered
    SLIDE_UP,       // slides up from bottom edge to centered
    ZOOM_IN,        // grows through font sizes 1 -> target, centered
    BOUNCE_IN       // slides in from left and overshoots/settles
};

// Fixed-size, POD request -- safe to copy across FreeRTOS tasks via a
// queue. (Arduino String is NOT safe to share across tasks this way.)
struct OledTextRequest {
    char payload[32];
    TextEffect effect;
};

// Owns the SSD1306 display and a dedicated FreeRTOS task that renders
// text + effects without ever blocking the caller (main loop, MQTT
// callback, etc). Call begin() once, then showText() from anywhere.
class OledController {
private:
public:
  OledController();
  ~OledController();
  void begin(const String &objectiveTopic);
  void handleMqttEvent(const String &topic, const String &payload);

  // Legacy direct-write API, kept for backward compatibility. Routes
  // through showText() with TextEffect::NONE -- do NOT touch `display`
  // directly anywhere else, the OLED task owns it exclusively.
  bool writeText(String payload);

  // Non-blocking: hands the request off to the OLED task via a queue and
  // returns immediately. Safe to call from any task, loop(), or an MQTT
  // callback. If called again before an animation finishes, the newer
  // call wins and the in-progress animation is interrupted.
  void showText(const String &payload, TextEffect effect = TextEffect::NONE);

  const String &topic() const { return _topic; }

private:
  String _topic;

  TwoWire i2c_oled;
  Adafruit_SSD1306* display;

  // ---- MQTT / business logic ---------------------------------------------
  // Interprets an incoming MQTT payload (JSON {"text","effect"}, or a
  // plain string as a fallback) into a request the render engine
  // understands. Knows nothing about drawing.
  OledTextRequest parseMqttPayload(const String &payload);
  static TextEffect effectFromString(const String &name);

  // ---- task / queue plumbing ---------------------------------------------
  QueueHandle_t textQueue = nullptr;
  TaskHandle_t  taskHandle = nullptr;

  static void oledTaskEntry(void *param);          // static trampoline for xTaskCreate
  void oledTaskLoop();                               // the actual task body
  void enqueueRequest(const OledTextRequest &req);   // shared by showText() and handleMqttEvent()
  bool runEffect(OledTextRequest &req);              // dispatches to the effectXxx() below
  bool sleepOrAbort(uint32_t ms, OledTextRequest &outNewReq); // interruptible vTaskDelay

  // ---- one function per effect --------------------------------------------
  // Each draws `payload` at `size` and returns true if interrupted mid-
  // animation by a fresher request (which is written into outNewReq).
  bool effectNone(const String &payload, uint8_t size, OledTextRequest &outNewReq);
  bool effectFlash(const String &payload, uint8_t size, OledTextRequest &outNewReq);
  bool effectTypewriter(const String &payload, uint8_t size, OledTextRequest &outNewReq);
  bool effectSlideInLeft(const String &payload, uint8_t size, OledTextRequest &outNewReq);
  bool effectSlideInRight(const String &payload, uint8_t size, OledTextRequest &outNewReq);
  bool effectSlideUp(const String &payload, uint8_t size, OledTextRequest &outNewReq);
  bool effectZoomIn(const String &payload, uint8_t size, OledTextRequest &outNewReq);
  bool effectBounceIn(const String &payload, uint8_t size, OledTextRequest &outNewReq);

  // ---- low-level drawing primitives, shared by every effect above -----
  uint8_t calcOptimalTextSize(const String &text, uint16_t *outW, uint16_t *outH);
  void drawCenteredAt(const String &text, uint8_t size, int16_t xOffset = 0, int16_t yOffset = 0);
};