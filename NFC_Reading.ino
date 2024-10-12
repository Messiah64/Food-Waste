#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <WebSocketsClient.h>

#define RST_PIN         22
#define SS_PIN          5
#define BUZZER_PIN      2  // Assume buzzer is connected to pin 2

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* websocket_server_host = "192.168.1.100"; // Replace with your server's IP
const uint16_t websocket_server_port = 8765;

MFRC522 mfrc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;
WebSocketsClient webSocket;

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

    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    // Connect to WebSocket server
    webSocket.begin(websocket_server_host, websocket_server_port, "/");
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);

    Serial.println(F("NFC Reader Ready. Tap a card to read."));
}

void loop() {
    webSocket.loop();

    String nfcData = readNFC();
    if (nfcData != "") {
        webSocket.sendTXT(nfcData);
        digitalWrite(BUZZER_PIN, HIGH);
        delay(100);
        digitalWrite(BUZZER_PIN, LOW);
    }
}

String readNFC() {
    // Look for new cards
    if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
        return "";
    }

    Serial.println(F("Card detected. Attempting to read..."));

    // Authenticate using key A
    MFRC522::StatusCode status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        Serial.println(F("Authentication failed"));
        return "";
    }

    // Read data
    byte buffer[18];
    byte size = sizeof(buffer);
    status = mfrc522.MIFARE_Read(blockAddr, buffer, &size);
    if (status != MFRC522::STATUS_OK) {
        Serial.println(F("Reading failed"));
        return "";
    }

    String result = "";
    for (byte i = 0; i < 16; i++) {
        result += (char)buffer[i];
    }

    Serial.println("Data read: " + result);

    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();

    return result;
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("WebSocket Disconnected");
            break;
        case WStype_CONNECTED:
            Serial.println("WebSocket Connected");
            break;
        case WStype_TEXT:
            Serial.println("Received text from server: " + String((char*)payload));
            break;
    }
}