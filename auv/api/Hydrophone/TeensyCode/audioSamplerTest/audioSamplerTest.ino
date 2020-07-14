/*
 * This one doesn't work, idk why... Nothing gets printed...
 *
 */
#include <Audio.h>

AudioInputI2S            i2s2;           //xy=105,63
AudioRecordQueue         queue1;         //xy=281,63
AudioConnection          patchCord1(i2s2, 0, queue1, 0);
AudioControlSGTL5000     sgtl5000_1;     //xy=265,212

void setup() {
  Serial.begin(9600);
  Serial.println("asdasd");
  // Audio connections require memory, and the record queue
  // uses this memory to buffer incoming audio.
  AudioMemory(60);

  // Enable the audio shield, select input, and enable output
  sgtl5000_1.enable();
  sgtl5000_1.inputSelect(AUDIO_INPUT_LINEIN);
  queue1.begin();
}


void loop() {
    byte buffer[512];
    memcpy(buffer, queue1.readBuffer(), 256);
    
    Serial.println("looper");
    for (int i = 0; i < 256; i++) {
      Serial.print("Byte is: ");
      Serial.print(buffer[i]);
    }
    
    delay(1000);
}
