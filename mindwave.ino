#include <SoftwareSerial.h>

SoftwareSerial BTSerial(7, 8);  // RX | TX

void setup() {
  Serial.begin(9600);
  BTSerial.begin(57600);
}

byte byteReadOneByte() {
  while (true) {
    if (BTSerial.available()) {
      return BTSerial.read();
    }
  }
  return 0;
}

void loop() {
  if (byteReadOneByte() == 170) {
    if (byteReadOneByte() == 170) {
      int iPayloadLength = byteReadOneByte();
      if (iPayloadLength > 169) {
        return;
      }

      byte byteGeneratedChecksum = 0;
      byte bytePayloadData[180] = {0};
      for (int i = 0; i < iPayloadLength; i++) {
        bytePayloadData[i] = byteReadOneByte();
        byteGeneratedChecksum += bytePayloadData[i];
      }
      byteGeneratedChecksum = 255 - byteGeneratedChecksum;

      byte byteChecksum = byteReadOneByte();
      if (byteChecksum == byteGeneratedChecksum) {
        for (int i = 0; i < iPayloadLength; i++) {
          switch (bytePayloadData[i]) {
            case 0x80: {
              short int raw = (bytePayloadData[i+2]<<8) | bytePayloadData[i+3];
              Serial.println(raw);
              Serial.println(",");
              i = i + 3;
              break;
            }
            case 0x83: {
              i = i + 25;
              break;
            }
            default: {
              break;
            }
          }
        }
      }
    }
  }
}
