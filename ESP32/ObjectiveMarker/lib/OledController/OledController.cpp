#include "OledController.h"
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define OLED_WIDTH 128
#define OLED_HEIGHT 32
 
bool OledController::run(uint8_t sdaPin, uint8_t sclPin, uint8_t i2cAddress) {
  // Wire.begin(sdaPin, sclPin);
  TwoWire I2C_OLED = TwoWire(1);
  Adafruit_SSD1306 display(OLED_WIDTH, OLED_HEIGHT, &I2C_OLED, -1);
  I2C_OLED.begin(33, 32, 400000); // 400kHz speed
  if (!display.begin(SSD1306_SWITCHCAPVCC, i2cAddress)) {
    Serial.printf("OledController: no display found at 0x%02X (check wiring/address)\n", i2cAddress);
    return false;
  }
  Serial.println("OledController: display found, drawing test pattern...");
 
  // Clear the buffer
  display.clearDisplay();

  // Draw text
  display.setTextSize(1);      // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE); // Draw white text
  display.setCursor(0, 0);     // Start at top-left corner
  display.println(F("Hello, Arduino!"));
  // display.fillScreen(SSD1306_WHITE);
  display.display();
  
  Serial.println("OledController: test pattern sent -- check the physical display now");
  return true;
}

void OledController::begin(const String &objectiveTopic) {
  _topic = objectiveTopic + "/oled_control";
}

void OledController::handleMqttEvent(const String &topic, const String &payload) {
  JsonDocument doc;
  if (deserializeJson(doc, payload)) {
    Serial.println("OledController: failed to parse JSON payload");
    return;
  }
  const char *text = doc["text"] | "";
  Serial.printf("OledController: would display '%s'\n", text);
  // TODO: display.clearDisplay(); display.println(text); display.display();
}
