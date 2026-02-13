#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

/* ---------- CONFIG ---------- */
const int SCAN_TIME = 2;  // seconds
const char* ROOM_NAME = "Front Door";

BLEScan* pBLEScan;

/* ---------- BLE CALLBACK ---------- */
class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {

    // Get BLE MAC address
    const char* mac = advertisedDevice.getAddress().toString().c_str();

    // Print to Serial in JSON format
    Serial.print("{\"item\":\"");
    Serial.print(mac);
    Serial.print("\",\"room\":\"");
    Serial.print(ROOM_NAME);
    Serial.println("\"}");
  }
};

/* ---------- SETUP ---------- */
void setup() {
  Serial.begin(115200);

  // Initialize BLE
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(false); // passive scan (uses less memory)
  pBLEScan->setInterval(50);
  pBLEScan->setWindow(49);

  Serial.println("BLE scanner initialized.");
}

/* ---------- LOOP ---------- */
void loop() {
  pBLEScan->start(SCAN_TIME, false);  // scan for SCAN_TIME seconds
  delay(1000);                         // short delay before next scan
}