#include "OledController.h"


#define OLED_WIDTH 128
#define OLED_HEIGHT 32
#define I2C_1 33
#define I2C_2 32
#define I2CADDRESS 0x3C
#define I2C_SPEED 400000


OledController::OledController()
  : i2c_oled(1) 
{
  
    display = new Adafruit_SSD1306(OLED_WIDTH, OLED_HEIGHT, &i2c_oled, -1);
}
  
OledController::~OledController()
{
  delete display;
}


bool OledController::writeText(String payload) {
  
  // Draw text
  display->setTextSize(1);      // Normal 1:1 pixel scale
  display->setTextColor(SSD1306_WHITE); // Draw white text
  display->setCursor(0, 0);     // Start at top-left corner
  display->println(payload);
  // display->fillScreen(SSD1306_WHITE);
  display->display();
  
  Serial.println("OledController: test pattern sent -- check the physical display now");
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
}

void OledController::handleMqttEvent(const String &topic, const String &payload) {
  // const char *text = doc["text"] | "";
  display->clearDisplay();
  Serial.printf("OledController: would display '%s'\n", payload.c_str());
  writeText(payload);  // SDA, SCL, I2C address
  // TODO: display.clearDisplay(); display.println(text); display.display();
}
