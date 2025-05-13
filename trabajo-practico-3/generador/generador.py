import json
import numpy as np
from datetime import datetime
import time
import paho.mqtt.client as mqtt

json_file = 'data/tweets1.json'
gap = 5

# Definir los parámetros del broker MQTT
broker = "kafka-mqtt"  # Usa el nombre de servicio o la IP de tu broker MQTT
port = 1883  # Puerto MQTT estándar
topic = "ktuits"
client_id = "generador"  # Un ID único para tu cliente MQTT

# Crear un cliente MQTT
client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

# Callback para cuando el cliente se conecta
def on_connect(client, userdata, flags, rc):
    print(f"Conectado con código {rc}")
    # Suscribirse al tema después de conectarse
    client.subscribe(topic,0)

# Callback para cuando un mensaje es recibido
def on_message(client, userdata, msg):
    print(f"Mensaje recibido en el tema {msg.topic}: {msg.payload.decode()}")

# Asignar los callbacks
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker MQTT
while True:
    try:
        client.connect(broker, port, 60)
        client.loop_start()  # Inicia el loop de escucha de MQTT
        print("Conectado al broker MQTT")
        break  # Si la conexión es exitosa, salir del bucle
    except Exception as e:
        print(f"Conexión fallida: {e}. Reintentando en 5 segundos...")
        time.sleep(5)  # Espera 5 segundos antes de reintentar

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

# Detener el cliente MQTT (en caso de que necesites finalizar el proceso)
client.loop_stop()  # Detener el loop de MQTT
client.disconnect()  # Desconectar del broker


#CREATE TABLE ktuits (
#  id STRING,
#  text STRING,
#  ts TIMESTAMP(3)
#) WITH (
#  'connector' = 'kafka',
#  'topic' = 'ktuits',
#  'properties.bootstrap.servers' = 'kafka:9092',
#  'format' = 'json',
#  'scan.startup.mode' = 'earliest-offset'
#);

#CREATE TABLE personalities (
#    id BIGINT,
#    mbti_personality STRING,
#    pers_id TINYINT
#) WITH (
#    'connector' = 'jdbc',
#    'url' = 'jdbc:mysql://mariadb:3306/ipmd',
#    'table-name' = 'mbti_labels',
#    'username' = 'wolfxyz',
#    'password' = 'wolfxyz',
#    'driver' = 'com.mysql.cj.jdbc.Driver'
#);



#Flink SQL> CREATE TABLE resultados (
#>   id STRING,
#>   tipo STRING,
#>   proba DOUBLE
#> ) WITH (
#>   'connector' = 'elasticsearch-7',
#>   'hosts' = 'http://elasticsearch:9200',
#>   'index' = 'resultados'
#> );
#>
#[INFO] Execute statement succeeded.