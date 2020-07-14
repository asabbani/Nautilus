/*
 * This sketch just blinks the LED on the Teensy to make sure it works.
 * 
 */

// The LED pin for the Teensy 4.1 is 13
int ledPin =  13;

// The setup() method runs once, when the sketch starts
void setup() {
  // Initialize pin 13 as an Output pin
  pinMode(ledPin, OUTPUT);
}

// the loop() method continously runs.
void loop() {
  digitalWrite(ledPin, HIGH);
  Serial.println("LED On!");
  delay(500);
  digitalWrite(ledPin, LOW);
  Serial.println("LED Off!");
  delay(500);
}
