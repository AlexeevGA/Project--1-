#include <WiFi.h>
#include <esp_now.h>

uint8_t senderMac[] = {0x64, 0xE8, 0x33, 0x8D, 0x6F, 0x4C};

#define MOTOR_PIN1 0
#define MOTOR_PIN2 1
#define OPT_PIN 5

typedef struct message {
  char msg[64];
} message;

message receivedMsg;

void controlMotor(String cmd) {
  if (cmd == "insert") {
    digitalWrite(MOTOR_PIN1, HIGH);
    digitalWrite(MOTOR_PIN2, LOW);
    Serial.println("Двигаться вперед");
  } 
  else if (cmd == "return") {
    digitalWrite(MOTOR_PIN1, LOW);
    digitalWrite(MOTOR_PIN2, HIGH);
    Serial.println("Двигаться назад");
  } 
  else {
    digitalWrite(MOTOR_PIN1, LOW);
    digitalWrite(MOTOR_PIN2, LOW);
    Serial.println("Остановка");
  }
}

void OnDataRecv(const esp_now_recv_info* info, const uint8_t* data, int len) {
  Serial.print("Получены данные от: ");
  for (int i = 0; i < 6; i++) {
    Serial.print(info->src_addr[i], HEX);
    if (i < 5) {
      Serial.print(":");
    }
  }
  Serial.println();

  memcpy(&receivedMsg, data, sizeof(receivedMsg));
  Serial.print("Полученное сообщение: ");
  Serial.println(receivedMsg.msg);

  if (strcmp(receivedMsg.msg, "insert") == 0) {
    controlMotor("insert");
  } 
  else if (strcmp(receivedMsg.msg, "return") == 0) {
    controlMotor("return");
  } 
  else {
    Serial.println("Неизвестная команда");
    controlMotor("stop");
  }
}

void ESP_NOWInit() {
  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Ошибка инициализации ESP-NOW");
    return;
  }

  esp_now_register_recv_cb(OnDataRecv);

  esp_now_peer_info_t peer = {};
  memcpy(peer.peer_addr, senderMac, 6);
  peer.channel = 0;
  peer.encrypt = false;

  if (esp_now_add_peer(&peer) != ESP_OK) {
    Serial.println("Ошибка добавления отправителя");
    return;
  }
}

void setup() {
  Serial.begin(9600);
  delay(1000);

  pinMode(MOTOR_PIN1, OUTPUT);
  pinMode(MOTOR_PIN2, OUTPUT);
  pinMode(OPT_PIN, INPUT);

  ESP_NOWInit();
  Serial.println("Ожидание сообщений...");
}

void loop() {
  if (digitalRead(OPT_PIN) == HIGH) {
    Serial.println("Оптопара сработала, останавливаем двигатель...");
    controlMotor("stop");
  }

  delay(100);
}