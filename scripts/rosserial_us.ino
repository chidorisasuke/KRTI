#include <ros.h>
#include <std_msgs/Float32.h>

const int trigPin = 5;   // Trig pin of the ultrasonic sensor
const int echoPin = 10;  // Echo pin of the ultrasonic sensor

ros::NodeHandle nh;

std_msgs::Float32 msg;
ros::Publisher chatter("/us", &msg);

void setup() {
  // Initialize serial communication
  Serial.begin(9600);

  // Set pin modes
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  nh.initNode();
  nh.advertise(chatter);
  
}

void loop() {
  long duration;
  float distance;
  
  // Clear the trigPin by setting it LOW
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Send a 10us pulse to trigPin to trigger the sensor
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read the echoPin, pulseIn returns the time in microseconds
  duration = pulseIn(echoPin, HIGH, 8542);

  // Calculate the distance in cm
  distance = duration * 0.0343 / 2;  // Speed of sound is ~343 m/s, so 0.0343 cm/us
  
  // Check for maximum distance limit
  if (distance <= 10){
    distance = 150;  // Set to 150 cm if distance is less than or equal to 10 cm
  }

  // Publish the distance to ROS
  msg.data = distance;
  chatter.publish(&msg);

  nh.spinOnce();
  delay(100);  // Add a small delay to avoid flooding the serial output
}
