// Define trigger and echo pins for the US-100 sensor in pulse mode
#define TRIGGER_PIN 5
#define ECHO_PIN 10

// Define maximum range in cm and corresponding timeout in microseconds
#define MAX_DISTANCE_CM 450 //set 400 for hcsr04
#define MAX_TIMEOUT_US (MAX_DISTANCE_CM * 2 / 0.0343) // Timeout for pulseIn

void setup() {
  // serial communication for monitoring
  Serial.begin(9600);
  
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Output a message to the serial monitor
  Serial.println("US-100 Ultrasonic Sensor in Pulse Mode");
}

void loop() {
  // Send a 10 microsecond pulse
  digitalWrite(TRIGGER_PIN, LOW); 
  delayMicroseconds(2);           
  digitalWrite(TRIGGER_PIN, HIGH); // Set the trigger pin HIGH for 10 microseconds
  delayMicroseconds(10);           
  digitalWrite(TRIGGER_PIN, LOW);  // Set the trigger pin LOW

  // Read the pulse duration from the echo pin, with a timeout to avoid hanging
  long duration = pulseIn(ECHO_PIN, HIGH, MAX_TIMEOUT_US);

  // If duration is 0, the echo was not received within the timeout
  if (duration == 0) {
    Serial.println("Out of range");
  } else {
    // Calculate the distance in centimeters (speed of sound is 343 m/s or 0.0343 cm/us)
    float distance_cm = (duration * 0.0343) / 2.0;

    // Check if the measured distance is within the valid range
    if (distance_cm >= 2.0 && distance_cm <= MAX_DISTANCE_CM) {
      
      Serial.print("Distance: ");
      Serial.print(distance_cm);
      Serial.println(" cm");
    } else {
      // error message for out-of-range values
      Serial.println("Measurement out of range");
    }
  }

  // Add a small delay before the next reading
  delay(100);
}
