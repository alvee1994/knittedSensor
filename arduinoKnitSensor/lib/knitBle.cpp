#include <knitBle.h>


BLEService sensorService("19B10010-E8F2-537E-4F6C-D104768A1214"); // create service
// create switch characteristic and allow remote device to read and write
BLEByteCharacteristic windowSize("19B10011-E8F2-537E-4F6C-D104768A1214", BLERead | BLEWrite);
// create button characteristic and allow remote device to get notifications
BLECharacteristic sensorReadings("19B10012-E8F2-537E-4F6C-D104768A1214",  BLERead | BLENotify, 512);


int pins = 4;
float sensors[4] = {0, 0, 0, 0};
int numReadings = 3;
int readings[3];
int resolution = 12;
int inputPin[4] = {A1, A2, A3, A4};
char data[10];

unsigned long time_us;
// unsigned long old_time;
// uint16_t time_since_;
// int count;


knitBle::knitBle(void){
  analogReadResolution(resolution);
  analogReference(AR_VDD);

  if (!BLE.begin()) {
  Serial.println("starting BLE failed!");
  while (1);
  }

  BLE.setLocalName("KneeBrace");  // set the name that is will appear as
  BLE.setAdvertisedService(sensorService);   // the uuid for the service this peripheral advertises

  sensorService.addCharacteristic(sensorReadings); // characteristics of the service
  sensorService.addCharacteristic(windowSize);
  // BLE.setEventHandler(BLEConnected, blePeripheralConnectHandler);
  // BLE.setEventHandler(BLEDisconnected, blePeripheralDisconnectHandler);
  BLE.addService(sensorService);
  BLE.advertise();

}

void knitBle::blePeripheralConnectHandler(BLEDevice central) {
  // central connected event handler
  Serial.print("Connected event, central: ");
  Serial.println(central.address());
}

void knitBle::blePeripheralDisconnectHandler(BLEDevice central) {
  // central disconnected event handler
  Serial.print("Disconnected event, central: ");
  Serial.println(central.address());
}

void knitBle::readSensors(){
  BLE.poll();
  float total[4] = {0, 0, 0, 0};
  for (int p = 0; p < pins; p++){
    for (int readIndex = 0; readIndex < numReadings; readIndex++){
        readings[readIndex] = analogRead(inputPin[p]);
        total[p] += readings[readIndex];
    }
    sensors[p] = total[p] / numReadings;
    sensors[p] = 1000 * 3.3 * (sensors[p] / pow(2, resolution));
  }
  broadcastReadings(sensors);
}

void knitBle::broadcastReadings(float *sensorData){

  int m = 0;
  for (int i = 0; i < pins; i++){
    int n = i * 2;
    data[n] = uint16_t(sensorData[i]) >> 8;
    data[n+1] = uint16_t(sensorData[i]) & 0xff;
  }

  sensorReadings.writeValue(data, sizeof(data));

}
