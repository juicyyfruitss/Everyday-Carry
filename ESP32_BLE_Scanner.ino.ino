#include <WiFi.h>
#include <PubSubClient.h>
#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

// ---- CONFIG ----
const char* ssid = "iPhone (4)";
const char* password = "Fluffy11";
const char* mqtt_server = "172.20.10.9"; // Pi 400 MQTT broker IP

const char* ROOM_NAME = "Bedroom";
const char* MQTT_TOPIC = "ble/bedroom";

WiFiClient espClient;
PubSubClient client(espClient);

BLEScan* pBLEScan;
int scanTime = 5; // seconds

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected");

  // Connect to MQTT
  client.setServer(mqtt_server, 1883);
  while (!client.connected()) {
    if (client.connect("esp32_scanner")) {
      Serial.println("MQTT connected");
    } else {
      delay(1000);
    }
  }

  // Initialize BLE scanner
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(true);
}

void loop() {

  BLEScanResults* foundDevices = pBLEScan->start(scanTime);

  for (int i = 0; i < foundDevices->getCount(); i++) {
    BLEAdvertisedDevice device = foundDevices->getDevice(i);
    String mac = device.getAddress().toString().c_str();
    String payload = "{\"item\":\"" + mac + "\",\"room\":\"Bedroom\"}"; // adjust room
    client.publish("ble/bedroom", payload.c_str());
  }

  pBLEScan->clearResults();
  delay(5000);
}