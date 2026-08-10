#include "AudioController.h"
#include <ArduinoJson.h>
#include "HardwareSerial.h"
#include <DFMiniMp3.h>

// Forward declare the notification class so we can reference the main object safely
class Mp3Notify;

// --- DFPlayer Mini Configuration (UART2 Pins 16 & 17) ---
// ESP32 HardwareSerial 2 defaults: RX2 = GPIO 16, TX2 = GPIO 17
#define FPS_RX 16
#define FPS_TX 17

// Target Serial2 globally to align with Pins 16 & 17


void AudioController::begin(const String &objectiveTopic) {
  _topic = objectiveTopic + "/audio_control";

  // Force Hardware Serial 2 setup with specific pins required by ESP32 before module init
  Serial2.begin(9600, SERIAL_8N1, FPS_RX, FPS_TX);
  
  // Clean initialization of the Makuna stack
  _mp3.begin();
}

void AudioController::handleMqttEvent(const String &topic, const String &payload) {
  JsonDocument doc;
  if (deserializeJson(doc, payload)) {
    Serial.println("AudioController: failed to parse JSON payload");
    return;
  }
  const char *soundFile = doc["sound_file"] | "";
  Serial.printf("AudioController: would play '%s'\n", soundFile);
  
  // Process the async loop structure required by Makuna
  _mp3.loop();
}

void AudioController::testPlay(const String &fileName)
{
  Serial.println(F("Connecting to DFPlayer..."));
  
  // Set lower volume baseline to insulate clone chip against brownouts
  _mp3.setVolume(20);  
  delay(500); // Critical delay for AB250S330Y to settle command registry
  
  Serial.println(F("DFPlayer Online! Attempting playback..."));
  
  // Plays track 0002 from your SD card's "mp3" folder using Makuna methods
  _mp3.playMp3FolderTrack(1);
  delay(500); // Final delay step to protect transmission cycle
  
  Serial.println(F("DFPlayer Finished Command Sequence!"));


  // Buzzer
  const int buzzerPin = 26; // Defines GPIO 26 for the buzzer
  pinMode(buzzerPin, OUTPUT); // Sets pin 26 as an output

  digitalWrite(buzzerPin, HIGH); // Turns the buzzer on
  delay(1000);                   // Waits for 1 second
  digitalWrite(buzzerPin, LOW);  // Turns the buzzer off
  delay(1000); 
    digitalWrite(buzzerPin, HIGH); // Turns the buzzer on
  delay(1000);                   // Waits for 1 second
  digitalWrite(buzzerPin, LOW);  // Turns the buzzer off
  delay(1000); 
  digitalWrite(buzzerPin, HIGH); // Turns the buzzer on
  delay(1000);                   // Waits for 1 second
  digitalWrite(buzzerPin, LOW);  // Turns the buzzer off
  delay(1000); 
}