#ifndef KNITBLE_H
#define KNITBLE_H

#include <ArduinoBLE.h>

class knitBle {       // The class
  public:             // Access specifier
    knitBle();
    void readSensors();
    void blePeripheralConnectHandler(BLEDevice central);
    void blePeripheralDisconnectHandler(BLEDevice central);

  private:
    void broadcastReadings(float *sensorData);
};

#endif
