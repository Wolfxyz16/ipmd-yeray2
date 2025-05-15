import json
import numpy as np
from datetime import datetime
import time
import paho.mqtt.client as mqtt

print("Starting generador.py")

json_file = 'data/tweets1.json'
gap = 5

# Definir los parámetros del broker MQTT
topic = "ktuits"
client_id = "generador"  # Un ID único para tu cliente MQTT

# Crear un cliente MQTT
client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

# Callback para cuando el cliente se conecta
def on_connect(client, userdata, flags, rc, properties):
    print(f"Conectado con código {rc}")
    # Suscribirse al tema después de conectarse
    client.subscribe(topic,0)

# Asignar los callbacks
client.on_connect = on_connect

# Conectar al broker MQTT
while True:
    try:
        client.connect("kafka-mqtt", 1883, 60)
        print("Conectado al broker MQTT")
        break  # Si la conexión es exitosa, salir del bucle
    except Exception as e:
        print(f"Conexión fallida: {e}. Reintentando en 5 segundos...")
        time.sleep(5)  # Espera 5 segundos antes de reintentar

client.loop_start()

# Abrir el archivo de tweets y publicarlos
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
            message = '{"user_id":' + str(tweets[user]["id"]) + ',"tweet":"' + text + '", "timestamp":"' + formatted + '"}'
            
            # Publicar el mensaje
            client.publish(topic, message)
            print(f"Mensaje enviado: {message}")
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        
        # Introducir un retraso entre las publicaciones
        time.sleep(gap)

# Detener el cliente MQTT (en caso de que se necesite finalizar el proceso)
client.loop_stop()  # Detener el loop de MQTT
client.disconnect()  # Desconectar del broker
