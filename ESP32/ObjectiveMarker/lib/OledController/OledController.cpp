#include "OledController.h"


#define OLED_WIDTH 128
#define OLED_HEIGHT 32
#define I2C_1 33
#define I2C_2 32
#define I2CADDRESS 0x3C
#define I2C_SPEED 400000
#define OLED_MARGIN 4 // px of breathing room around auto-sized text


// Tunable timing/step constants for each effect. Pulled out of the effect
// bodies so the "feel" of an animation can be adjusted here without
// hunting through the rendering logic.
namespace {
  constexpr uint8_t  FLASH_BLINK_COUNT        = 4;
  constexpr uint32_t FLASH_INTERVAL_MS        = 150;

  constexpr uint32_t TYPEWRITER_CHAR_DELAY_MS = 60;

  constexpr int16_t  SLIDE_STEP_PX            = 16;
  constexpr uint32_t SLIDE_STEP_DELAY_MS      = 15;

  constexpr int16_t  SLIDE_UP_STEP_PX         = 8;
  constexpr uint32_t SLIDE_UP_STEP_DELAY_MS   = 20;

  constexpr uint32_t ZOOM_STEP_DELAY_MS       = 120;

  constexpr uint32_t BOUNCE_STEP_DELAY_MS     = 70;
  constexpr int16_t  BOUNCE_KEYFRAMES[]       = { -80, -20, 10, -4, 0 };
}


OledController::OledController()
  : i2c_oled(1)
{

    display = new Adafruit_SSD1306(OLED_WIDTH, OLED_HEIGHT, &i2c_oled, -1);
}

OledController::~OledController()
{
  if (taskHandle != nullptr) {
    vTaskDelete(taskHandle);
  }
  if (textQueue != nullptr) {
    vQueueDelete(textQueue);
  }
  delete display;
}


bool OledController::writeText(String payload) {
  // Routed through the non-blocking effect engine so `display` is only
  // ever touched from the OLED task. Kept for backward compatibility with
  // existing callers.
  showText(payload, TextEffect::NONE);
  return true;
}

void OledController::begin(const String &objectiveTopic) {
  _topic = objectiveTopic + "/oled_control";

  i2c_oled.begin(I2C_1, I2C_2, I2C_SPEED); // 400kHz speed
  if (!display->begin(SSD1306_SWITCHCAPVCC, I2CADDRESS)) {
    Serial.printf("OledController: no display found at 0x%02X (check wiring/address)\n", I2CADDRESS);
  }
  Serial.println("OledController: display found, drawing test pattern...");
  // Clear the buffer
  display->clearDisplay();
  display->display();

  // Spin up the non-blocking effect engine. Depth-1 queue: only the
  // latest showText() call matters, so a fresh call always overwrites
  // any request the task hasn't picked up yet.
  textQueue = xQueueCreate(1, sizeof(OledTextRequest));

  xTaskCreatePinnedToCore(
      oledTaskEntry,   // task function
      "OledTask",      // name (for debugging)
      4096,             // stack size in bytes -- bump if you see stack overflow warnings
      this,             // param passed to the task (this instance)
      1,                // priority -- low-ish, this is UI, not time-critical
      &taskHandle,
      1                 // core 1 (APP core), leaves core 0 free for WiFi/MQTT
  );
}

// ============================================================================
// MQTT / business logic
// Purely about interpreting the incoming message. No drawing, no display
// access -- this could be unit tested without any hardware attached.
// ============================================================================

// Maps a JSON "effect" string to a TextEffect. Unknown or missing names
// fall back to TextEffect::NONE.
TextEffect OledController::effectFromString(const String &name) {
  if (name == "flash")        return TextEffect::FLASH;
  if (name == "typewriter")   return TextEffect::TYPEWRITER;
  if (name == "slide_left")   return TextEffect::SLIDE_IN_LEFT;
  if (name == "slide_right")  return TextEffect::SLIDE_IN_RIGHT;
  if (name == "slide_up")     return TextEffect::SLIDE_UP;
  if (name == "zoom")         return TextEffect::ZOOM_IN;
  if (name == "bounce")       return TextEffect::BOUNCE_IN;
  return TextEffect::NONE;
}

// Accepts either {"text": "...", "effect": "flash"} JSON or a plain string
// payload (treated as text with no effect). Always returns a valid,
// truncated-to-fit request.
OledTextRequest OledController::parseMqttPayload(const String &payload) {
  OledTextRequest req;
  req.effect = TextEffect::NONE;

  JsonDocument doc; // ArduinoJson v7: replaces StaticJsonDocument<N>
  DeserializationError err = deserializeJson(doc, payload);

  if (!err && doc["text"].is<const char *>()) {
    const char *text = doc["text"];
    const char *effectName = doc["effect"] | "none";
    strncpy(req.payload, text, sizeof(req.payload) - 1);
    req.effect = effectFromString(String(effectName));
  } else {
    strncpy(req.payload, payload.c_str(), sizeof(req.payload) - 1);
  }
  req.payload[sizeof(req.payload) - 1] = '\0';

  return req;
}

void OledController::handleMqttEvent(const String &topic, const String &payload) {
  OledTextRequest req = parseMqttPayload(payload);
  Serial.printf("OledController: would display '%s' (effect: %d)\n", req.payload, (int)req.effect);
  enqueueRequest(req);
}

// ============================================================================
// Task / queue plumbing
// ============================================================================

// Public, non-blocking API. Builds a request and hands it to the same
// enqueue path handleMqttEvent() uses.
void OledController::showText(const String &payload, TextEffect effect) {
  OledTextRequest req;
  strncpy(req.payload, payload.c_str(), sizeof(req.payload) - 1);
  req.payload[sizeof(req.payload) - 1] = '\0';
  req.effect = effect;

  enqueueRequest(req);
}

// xQueueOverwrite always succeeds immediately on a length-1 queue -- this
// never blocks the caller, even if the OLED task is mid-animation.
void OledController::enqueueRequest(const OledTextRequest &req) {
  xQueueOverwrite(textQueue, &req);
}

// Static trampoline required by xTaskCreate's C function-pointer signature.
void OledController::oledTaskEntry(void *param) {
  static_cast<OledController *>(param)->oledTaskLoop();
}

// The task body. Blocks (yielding the CPU, not busy-waiting) until a
// request arrives, runs its effect, then waits for the next one. If an
// effect gets interrupted by a fresher request, it loops straight into
// that new request without going back to the outer wait.
void OledController::oledTaskLoop() {
  OledTextRequest req;

  // Wait forever for the first-ever request.
  xQueueReceive(textQueue, &req, portMAX_DELAY);

  for (;;) {
    bool interrupted = runEffect(req); // req is overwritten with the new one if interrupted
    if (!interrupted) {
      xQueueReceive(textQueue, &req, portMAX_DELAY);
    }
    // else: fall straight back into runEffect() with the new req
  }
}

// Interruptible sleep. Waits up to `ms` for a new request. If one arrives,
// fills outNewReq and returns true (caller should abort its animation). If
// it times out with nothing new, returns false (caller continues). This
// IS the vTaskDelay -- but one that can be preempted by fresh text.
bool OledController::sleepOrAbort(uint32_t ms, OledTextRequest &outNewReq) {
  return xQueueReceive(textQueue, &outNewReq, pdMS_TO_TICKS(ms)) == pdTRUE;
}

// Looks up the right effect function for the request and runs it. This is
// the only place that knows the enum-to-function mapping.
bool OledController::runEffect(OledTextRequest &req) {
  String payload(req.payload);
  uint16_t w, h;
  uint8_t size = calcOptimalTextSize(payload, &w, &h);
  display->setTextColor(SSD1306_WHITE);

  OledTextRequest newReq;
  bool interrupted = false;

  switch (req.effect) {
    case TextEffect::NONE:           interrupted = effectNone(payload, size, newReq); break;
    case TextEffect::FLASH:          interrupted = effectFlash(payload, size, newReq); break;
    case TextEffect::TYPEWRITER:     interrupted = effectTypewriter(payload, size, newReq); break;
    case TextEffect::SLIDE_IN_LEFT:  interrupted = effectSlideInLeft(payload, size, newReq); break;
    case TextEffect::SLIDE_IN_RIGHT: interrupted = effectSlideInRight(payload, size, newReq); break;
    case TextEffect::SLIDE_UP:       interrupted = effectSlideUp(payload, size, newReq); break;
    case TextEffect::ZOOM_IN:        interrupted = effectZoomIn(payload, size, newReq); break;
    case TextEffect::BOUNCE_IN:      interrupted = effectBounceIn(payload, size, newReq); break;
  }

  if (interrupted) {
    req = newReq;
  }
  return interrupted;
}

// ============================================================================
// Effects -- one function each. Every effect follows the same shape: draw
// a frame, display it, then sleepOrAbort() before the next frame. Any
// sleepOrAbort() that returns true means abandon ship immediately.
// ============================================================================

bool OledController::effectNone(const String &payload, uint8_t size, OledTextRequest &outNewReq) {
  display->clearDisplay();
  drawCenteredAt(payload, size);
  display->display();
  return false;
}

bool OledController::effectFlash(const String &payload, uint8_t size, OledTextRequest &outNewReq) {
  for (uint8_t i = 0; i < FLASH_BLINK_COUNT; i++) {
    display->clearDisplay();
    if (i % 2 == 0) drawCenteredAt(payload, size);
    display->display();
    if (sleepOrAbort(FLASH_INTERVAL_MS, outNewReq)) return true;
  }
  // End lit, regardless of how many blinks happened.
  display->clearDisplay();
  drawCenteredAt(payload, size);
  display->display();
  return false;
}

bool OledController::effectTypewriter(const String &payload, uint8_t size, OledTextRequest &outNewReq) {
  // Reveal one character at a time, keeping the final centered position
  // fixed so the text doesn't jitter as it grows.
  int16_t x1, y1;
  uint16_t fullW, fullH;
  display->setTextSize(size);
  display->getTextBounds(payload, 0, 0, &x1, &y1, &fullW, &fullH);
  int16_t startX = ((OLED_WIDTH - (int16_t)fullW) / 2) - x1;
  int16_t startY = ((OLED_HEIGHT - (int16_t)fullH) / 2) - y1;

  for (uint16_t i = 1; i <= payload.length(); i++) {
    display->clearDisplay();
    display->setTextSize(size);
    display->setCursor(startX, startY);
    display->print(payload.substring(0, i));
    display->display();
    if (sleepOrAbort(TYPEWRITER_CHAR_DELAY_MS, outNewReq)) return true;
  }
  return false;
}

bool OledController::effectSlideInLeft(const String &payload, uint8_t size, OledTextRequest &outNewReq) {
  for (int16_t off = -(OLED_WIDTH); off <= 0; off += SLIDE_STEP_PX) {
    display->clearDisplay();
    drawCenteredAt(payload, size, off, 0);
    display->display();
    if (sleepOrAbort(SLIDE_STEP_DELAY_MS, outNewReq)) return true;
  }
  // Guarantee the final frame is exactly centered even if the step size
  // didn't land precisely on 0.
  display->clearDisplay();
  drawCenteredAt(payload, size);
  display->display();
  return false;
}

bool OledController::effectSlideInRight(const String &payload, uint8_t size, OledTextRequest &outNewReq) {
  for (int16_t off = OLED_WIDTH; off >= 0; off -= SLIDE_STEP_PX) {
    display->clearDisplay();
    drawCenteredAt(payload, size, off, 0);
    display->display();
    if (sleepOrAbort(SLIDE_STEP_DELAY_MS, outNewReq)) return true;
  }
  display->clearDisplay();
  drawCenteredAt(payload, size);
  display->display();
  return false;
}

bool OledController::effectSlideUp(const String &payload, uint8_t size, OledTextRequest &outNewReq) {
  for (int16_t off = OLED_HEIGHT; off >= 0; off -= SLIDE_UP_STEP_PX) {
    display->clearDisplay();
    drawCenteredAt(payload, size, 0, off);
    display->display();
    if (sleepOrAbort(SLIDE_UP_STEP_DELAY_MS, outNewReq)) return true;
  }
  display->clearDisplay();
  drawCenteredAt(payload, size);
  display->display();
  return false;
}

bool OledController::effectZoomIn(const String &payload, uint8_t size, OledTextRequest &outNewReq) {
  // Grow through each font size up to the target, each centered.
  for (uint8_t s = 1; s <= size; s++) {
    display->clearDisplay();
    drawCenteredAt(payload, s);
    display->display();
    if (sleepOrAbort(ZOOM_STEP_DELAY_MS, outNewReq)) return true;
  }
  return false;
}

bool OledController::effectBounceIn(const String &payload, uint8_t size, OledTextRequest &outNewReq) {
  // Slide in from the left, overshoot past center, settle back.
  for (int16_t off : BOUNCE_KEYFRAMES) {
    display->clearDisplay();
    drawCenteredAt(payload, size, off, 0);
    display->display();
    if (sleepOrAbort(BOUNCE_STEP_DELAY_MS, outNewReq)) return true;
  }
  return false;
}

// ============================================================================
// Low-level drawing primitives -- shared by every effect above. Pure
// "technical" layer: sizing and positioning math, no notion of animation
// or business meaning.
// ============================================================================

// Finds the largest standard GFX font size (1-4) whose bounding box fits
// within the screen (minus margin). Writes the resulting pixel width/height
// of the text at that size into outW/outH.
uint8_t OledController::calcOptimalTextSize(const String &text, uint16_t *outW, uint16_t *outH) {
  int16_t x1, y1;
  uint16_t w = 0, h = 0;

  for (uint8_t size = 4; size >= 1; size--) {
    display->setTextSize(size);
    display->getTextBounds(text, 0, 0, &x1, &y1, &w, &h);
    if (w <= (OLED_WIDTH - OLED_MARGIN) && h <= (OLED_HEIGHT - 2)) {
      *outW = w;
      *outH = h;
      return size;
    }
  }
  display->setTextSize(1);
  display->getTextBounds(text, 0, 0, &x1, &y1, &w, &h);
  *outW = w;
  *outH = h;
  return 1;
}

void OledController::drawCenteredAt(const String &text, uint8_t size, int16_t xOffset, int16_t yOffset) {
  int16_t x1, y1;
  uint16_t w, h;
  display->setTextSize(size);
  display->getTextBounds(text, 0, 0, &x1, &y1, &w, &h);

  int16_t x = ((OLED_WIDTH - (int16_t)w) / 2) - x1 + xOffset;
  int16_t y = ((OLED_HEIGHT - (int16_t)h) / 2) - y1 + yOffset;

  display->setCursor(x, y);
  display->print(text);
}