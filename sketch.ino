// SPDX-FileCopyrightText: Copyright (C) 2025 ARDUINO SA <http://www.arduino.cc>
//
// SPDX-License-Identifier: MPL-2.0

#include "Arduino_RouterBridge.h"

const int INPUT_PIN = 2;

unsigned long previousMillis = 0;
unsigned long logMillis = 0;

const long blinkInterval = 500;
const long logInterval = 5000;  // Log every 5 seconds

bool ledState = HIGH;

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(INPUT_PIN, INPUT_PULLDOWN);
    digitalWrite(LED_BUILTIN, HIGH);
    
    Bridge.begin();
    
    // Provide functions callable from Python
    Bridge.provide("get_pin_state", get_pin_state);
    Bridge.provide("get_led_state", get_led_state);
}

void loop() {
    unsigned long currentMillis = millis();
    
    // Read input and control LED
    bool inputHigh = digitalRead(INPUT_PIN);
    
    if (inputHigh == HIGH) {
        // Blink the LED
        if (currentMillis - previousMillis >= blinkInterval) {
            previousMillis = currentMillis;
            ledState = !ledState;
            digitalWrite(LED_BUILTIN, ledState);
        }
    } else {
        // LED off
        digitalWrite(LED_BUILTIN, HIGH);
    }
    
    // Send data to Python for logging every 5 seconds
    if (currentMillis - logMillis >= logInterval) {
        logMillis = currentMillis;
        
        // Send event to Python side
        Bridge.call("log_data", inputHigh, ledState == LOW);
    }
}

// Functions callable from Python
bool get_pin_state() {
    return digitalRead(INPUT_PIN);
}

bool get_led_state() {
    return digitalRead(LED_BUILTIN) == LOW;  // Return true if LED is on
}