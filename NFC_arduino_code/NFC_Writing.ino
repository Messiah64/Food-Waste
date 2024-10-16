#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN         22
#define SS_PIN          5
#define BUZZER_PIN      2  // Assume buzzer is connected to pin 2

MFRC522 mfrc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;
constexpr byte sector         = 1;
constexpr byte blockAddr      = 4;
constexpr byte trailerBlock   = 7;

void setup() {
    Serial.begin(115200);
    while (!Serial);
    SPI.begin();
    mfrc522.PCD_Init();
    pinMode(BUZZER_PIN, OUTPUT);

    // Prepare the key (used both as key A and as key B)
    for (byte i = 0; i < 6; i++) {
        key.keyByte[i] = 0xFF;
    }

    Serial.println(F("NFC Writer Ready. Enter data to write:"));
}

void loop() {
    if (Serial.available()) {
        String dataToWrite = Serial.readStringUntil('\n');
        writeNFC(dataToWrite);
    }
}

void writeNFC(String data) {
    // Wait for a new card
    if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
        return;
    }

    Serial.println(F("Card detected. Attempting to write..."));

    // Authenticate using key A
    MFRC522::StatusCode status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        Serial.println(F("Authentication failed"));
        return;
    }

    // Write data
    byte buffer[16];
    data.getBytes(buffer, 16);
    status = mfrc522.MIFARE_Write(blockAddr, buffer, 16);
    if (status != MFRC522::STATUS_OK) {
        Serial.println(F("Writing failed"));
        return;
    }

    Serial.println(F("Data written successfully"));
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);

    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
}