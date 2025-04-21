import json
import numpy as np
from datetime import datetime
import time
import paho.mqtt.client as mqtt

json_file = 'data/tweets1.json'
gap = 5

# Definir los parámetros del broker MQTT
broker = "mqtt.eclipse.org"  # Cambia esta URL por la del broker que estés usando
port = 1883  # Puerto MQTT estándar (puedes usar otro si es necesario)
topic = "mi/tema/eventos"  # El tema al que deseas publicar el mensaje
client_id = "generador"  # Un ID único para tu cliente MQTT

client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

with open(json_file, 'r') as file:
    tweets = json.load(file)
    while True:
        try:
            user = np.random.randint(len(tweets))
            tweet = np.random.randint(len(tweets[user]["tweets"]))
            now = datetime.now()
            formatted = now.strftime("%Y-%m-%d %H:%M:%S")
            text = tweets[user]["tweets"][tweet].encode('utf-8','ignore').decode("utf-8").replace('\n', ' ')
            text += "."
            text = text.replace('"', "")
            text = text.replace('\\', "")
            print('{"user_id":' + str(tweets[user]["id"]) + ',"tweet":"' + text + '", "timestamp":"' + formatted + '"}')
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        # Introduce a delay between insertions
        time.sleep(gap)
            
print("Exiting...")
