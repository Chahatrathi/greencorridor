#include <WiFi.h>
#include <WebServer.h>
#include "config.h"

WebServer server(80);

// Function to reset all lights to OFF
void allLightsOff() {
  digitalWrite(RED_LED, LOW);
  digitalWrite(YELLOW_LED, LOW);
  digitalWrite(GREEN_LED, LOW);
}

void setup() {
  Serial.begin(115200);
  
  pinMode(RED_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  // Initialize with Red Light (Standard safety)
  allLightsOff();
  digitalWrite(RED_LED, HIGH);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nHardware Sync Active");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Endpoint: Software calls this to turn light GREEN
  server.on("/set_green", HTTP_GET, []() {
    allLightsOff();
    digitalWrite(GREEN_LED, HIGH);
    server.send(200, "text/plain", "Hardware: Light is now GREEN");
    Serial.println("Command Received: Switching to GREEN");
  });

  // Endpoint: Software calls this to turn light RED
  server.on("/set_red", HTTP_GET, []() {
    allLightsOff();
    digitalWrite(RED_LED, HIGH);
    server.send(200, "text/plain", "Hardware: Light is now RED");
    Serial.println("Command Received: Switching to RED");
  });

  server.begin();
}

void loop() {
  server.handleClient(); // Constantly listens for requests from your Python app
}