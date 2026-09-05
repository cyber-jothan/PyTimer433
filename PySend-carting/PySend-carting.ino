#include <RCSwitch.h>

RCSwitch mySwitch = RCSwitch();

void setup() {
  Serial.begin(9600);
  mySwitch.enableTransmit(10);  // Transmitter pin 10
}

void loop() {
  if (Serial.available()) {
    String received = Serial.readStringUntil('\n');
    received.trim();
    
    int colonIndex = received.indexOf(':');
    if (colonIndex != -1) {
      String codeStr = received.substring(0, colonIndex);
      int pulseLength = received.substring(colonIndex + 1).toInt();
      
      if (pulseLength > 0) {
        mySwitch.setPulseLength(pulseLength);
        mySwitch.send(codeStr.c_str());  // Sends as binary (0/1 string)
        Serial.println("Signal sent: " + codeStr + ":" + String(pulseLength));
      }
    }
  }
}

//
//#include <RCSwitch.h>
//
//RCSwitch mySwitch = RCSwitch();
//
//void setup() {
//  Serial.begin(9600);
//  mySwitch.enableTransmit(10);
//  mySwitch.setPulseLength(348);  // Matches your original timing
//  // mySwitch.setProtocol(1);
//  // mySwitch.setRepeatTransmit(10);
//  Serial.println("Ready - Sending hardcoded code repeatedly");
//}
//
//void loop() {
//  // Serial input disabled - hardcoded transmission only
//  
//  const char* hardcodedCode = "001011000001100101101000";
//  Serial.print("Sending: ");
//  Serial.println(hardcodedCode);
//  
//  mySwitch.send(hardcodedCode);
//  delay(2000);
//}
