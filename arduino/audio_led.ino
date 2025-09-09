// Audio-Responsive LED Controller (Simple Version)
// Controls a single LED synchronized to audio brightness data

#include "brightness_data.h"
#include <avr/pgmspace.h> 

const int LED_PIN = 9;        // Audio-responsive LED pin (PWM)
const int BUTTON_PIN = 10;    // Button to start sequence

unsigned long start = 0;
bool buttonPressed = false;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  // Check if button is pressed to start sequence
  if (digitalRead(BUTTON_PIN) == LOW && !buttonPressed) {
    buttonPressed = true;
    start = millis();
  }

  if (buttonPressed) {
    // Control audio-responsive LED
    unsigned long elapsed = millis() - start;
    int index = elapsed / ms;
    
    if (index >= arraySize) {
      // Reset when audio data is complete
      buttonPressed = false;
      digitalWrite(LED_PIN, LOW);
    } else {
      int brightness = pgm_read_byte(&brightnessArray[index]);
      analogWrite(LED_PIN, brightness);
    }
  }
}