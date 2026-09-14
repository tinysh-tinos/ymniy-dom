import paho.mqtt.client as mqtt
import csv

def on_connect(client, userdata, flags, rc, properties=None):
    client.subscribe("esp8266/sensordata")

def on_message(client, userdata, msg):
    data = msg.payload.decode('utf-8')  # data
    print(data)
    with open('data/data.csv', mode='w', newline='', encoding='utf-8') as file:
      writer = csv.writer(file)
      writer.writerow(data)

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()
