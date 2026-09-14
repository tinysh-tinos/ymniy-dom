#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "abc";
const char* password = "123qwe";
const char* mqtt_server = "192.168.1.100"; 
const int mqtt_port = 1883;
const char* mqtt_topic = "esp8266/sensordata";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
int sensorValue = 0;

#define temp_kitchen 2 

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Подключение к ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi подключен");
  Serial.print("IP адрес Wemos: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Ожидание подключения к MQTT...");
    if (client.connect("WemosD1MiniClient")) {
      Serial.println("подключено!");
    } else {
      Serial.print("ошибка, rc=");
      Serial.print(client.state());
      Serial.println(" повтор через 5 секунд");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(temp_kitchen, INPUT);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 5000) {
    lastMsg = now;

    sensorValue = digitalRead(temp_kitchen);

    char msg[50];
    snprintf(msg, sizeof(msg), "%d", sensorValue);
    
    Serial.print("Отправка сообщения: ");
    Serial.println(msg);
    
    client.publish(mqtt_topic, msg);
  }
}
