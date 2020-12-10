#include <knitBle.h>

knitBle* kneeBrace;

void setup() {
  // initialize serial communication with computer:
  Serial.begin(9600);

  knitBle kb;
  kneeBrace = &kb;
  
}



void loop() {
  kneeBrace->readSensors();
}
