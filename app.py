import paho.mqtt.client as mqtt
import csv
import json
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify

CSV_FILE = 'data/data.csv'
CSV_LOCK = threading.Lock()
LATEST = {}

app = Flask(__name__)


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"MQTT connected: {rc}")
    client.subscribe("esp8266/+/data")
    client.subscribe("esp8266/sensordata")


def on_message(client, userdata, msg):
    raw = msg.payload.decode('utf-8')
    print(f"[{msg.topic}] {raw}")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {"raw": raw}

    device_id = payload.get("id")
    if not device_id:
        parts = msg.topic.split("/")
        device_id = parts[1] if len(parts) >= 3 else "unknown"

    payload["id"] = device_id
    payload["timestamp"] = datetime.now().isoformat(timespec="seconds")

    LATEST[device_id] = payload

    with CSV_LOCK:
        file_exists = False
        try:
            with open(CSV_FILE, 'r', encoding='utf-8'):
                file_exists = True
        except FileNotFoundError:
            pass

        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
            fields = ["timestamp", "id", "temp", "hum", "raw"]
            writer = csv.DictWriter(f, fieldnames=fields)
            if not file_exists:
                writer.writeheader()
            writer.writerow({k: payload.get(k, "") for k in fields})


def start_mqtt():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_forever()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    return jsonify(LATEST)


if __name__ == "__main__":
    threading.Thread(target=start_mqtt, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
