# Trabajo práctico 2. Yeray Carretero y Yeray Li.

## Estructura del proyecto


>!Hay que cambiar 
```bash
├── config
├── db
│   └── init.sql
├── docker-compose.yaml
├── ejecutor
│   ├── Dockerfile
│   ├── export_to_mariadb.py
│   ├── init.sh
│   └── requeriments.txt
├── hive
│   ├── Dockerfile
│   └── init_hive.sql
├── namenode
│   ├── Dockerfile
│   └── init_hdfs.sh
├── estructura
│   └── userdata.avsc
└── userdata
    ├── userdata1.avro
    ├── userdata2.avro
    ├── userdata3.avro
    ├── userdata4.avro
    └── userdata5.avro
```

* `docker-compose.yaml`: Orquesta todos los servicios (BD, Flink, Generador, Elasticsearch, etc.) en contenedores.
* `/jars`: Carpeta en la que almacenaremos los archivos .jar para configurar la conexion entre contenedores.


* `db/init.sql`: Script SQL que inicializa la base de datos y crea las tablas necesarias. En este trabajo, las tablas creadas son para asegurar la implementación tanto de grafana como de superset

* `generador.py`: Script para la ejecución del contenedor que va a generar los tweets y publicarlos en el topic ktuits.

* `download-data.sh`: Script que nos permite descargar los datos con los que vamos a trabajar en un solo paso.


Ahora vamos a explicar que hace cada servicio que se detallada en el archivo `docker-compose.yaml` y los archivos que lo componen.

## Servicio generador

El contenedor ejecutara un archivo Python que sera el encargado de generar eventos – cada tuit es un evento – estos serán enviados a un tema MQTT. Los mensajes enviados a ese tema serán automáticamente reenviados a un clúster Kafka. 

### [`generador/Dockerfile`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-3/generador/Dockerfile) 

Imagen del contendor.

```Dockerfile
FROM python:3

WORKDIR /trabajo-practico-3

COPY generador/requeriments.txt .
RUN pip install --no-cache-dir -r requeriments.txt

COPY ./generador/generador.py .
RUN chmod +x ./generador.py


CMD [ "sh", "-c", "sleep 10 && python generador.py" ]
```

### [`generador/generador.py`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-3/generador/generador.py)

Script que generara los eventos.

```py
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

# Detener el cliente MQTT (en caso de que se necesite finalizar el proceso)
client.loop_stop()  # Detener el loop de MQTT
client.disconnect()  # Desconectar del broker

```


## Servicios Zookeper, Flink, Kafka, etc.

### Zookeper

El servicio zookeeper actúa como coordinador central en sistemas distribuidos. Proporciona un servicio de nombres, sincronización y gestión de configuración para aplicaciones distribuidas como Kafka o HDFS. Su función principal es garantizar la coherencia y disponibilidad de la información compartida entre nodos.

```yaml
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.1
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
```

### Kafka

El servicio kafka es una plataforma de mensajería distribuida utilizada para construir pipelines de datos y sistemas de transmisión en tiempo real. Funciona como intermediario entre productores y consumidores de mensajes, garantizando durabilidad y tolerancia a fallos. Este contenedor se conecta a Zookeeper para coordinarse y escucha conexiones en el puerto 9092, usado por productores y consumidores Kafka.

```yaml
  kafka:
    image: confluentinc/cp-kafka:7.4.1
    container_name: kafka
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT

```

### Kafka-MQTT

El servicio kafka-mqtt actúa como un puente entre el protocolo MQTT y Apache Kafka. Permite recibir datos publicados por dispositivos o clientes MQTT y redirigirlos automáticamente a un tema Kafka. Este contenedor es clave para integrar flujos de datos de sensores u otros sistemas embebidos con plataformas de análisis como Flink o Elasticsearch.

```yaml
  kafka-mqtt:
    image: confluentinc/cp-kafka-mqtt:7.4.1
    container_name: kafka-mqtt
    environment:
      KAFKA_MQTT_BOOTSTRAP_SERVERS: kafka:9092
      KAFKA_MQTT_TOPIC_REGEX_LIST: tuits:ktuits
      KAFKA_MQTT_LICENSE_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_MQTT_CONFLUENT_TOPIC_REPLICATION_FACTOR: 1 
    ports:
      - "1883:1883"
    depends_on:
      - kafka
```

### Elasticsearch

El servicio elasticsearch es un motor de búsqueda y análisis distribuido. Indexa y almacena datos estructurados en documentos JSON, permitiendo búsquedas rápidas y complejas en grandes volúmenes de información. Este contenedor escucha por defecto en el puerto 9200, y forma la base del stack ELK (Elasticsearch, Logstash, Kibana) para análisis de logs y datos en tiempo real.

```yaml
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - cluster.name=docker-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - discovery.type=single-node
    ports:
      - "9200:9200"
      - "9300:9300"
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
```

### Mariadb

En el servicio de Mariadb hay alojada un servidor mariadb que se encarga de almacenar toda la información. Cuando una instancia web recibe una petición REST, esta se comunica con el servidor para llevar a cabo la tarea. A la hora de crear el contenedor, le pasamos los datos `mbti_labels.csv` montamos un volumen en el directorio `/docker-entrypoint-initdb.d/`. Dentro del volumen le pasamos un pequeño script sql para que el servidor ejecutará al iniciarse. Dentro del script creamos la base de datos, definimos las tablas, creamos los usuarios y definimos los permisos para que solo puedan acceder a la base de datos de la aplicación.

```yaml
  mariadb:
    image: mariadb
    container_name: mariadb
    restart: always
    ports:
      - "3306:3306"
    volumes:
      - ./db:/docker-entrypoint-initdb.d/:ro
      - ./data/mbti_labels.csv:/var/lib/mysql/mbti_labels.csv
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_USER: wolfxyz
      MYSQL_PASSWORD: wolfxyz
      MYSQL_DATABASE: ipmd

```

El servicio mariadb contiene el servidor donde se ejecuta el SGBD mariadb. Indicamos la imagen de mariadb, definimos el nombre y que cuando el servicio se caiga o docker se detenga (`restart: always`). En la línea de puerto mapeamos el puerto 3306 con el puerto 3306 de nuestro ordenador. En volumenes le indicamos el directorio  `./db` de nuestro repositorio, en el encontramos un script que el servidor ejecutará cada vez que se inicie.

En la línea de `environment` le indicamos al contenedor las variables de entorno que tiene que tener sus sistema operativo. En nuestro caso nos ayudan a pre-configurar el servidor mariadb.

### Kibana

El servicio kibana proporciona una interfaz web para visualizar y explorar los datos almacenados en Elasticsearch. Permite construir dashboards, realizar búsquedas, aplicar filtros y explorar temporalmente los datos. Este contenedor se conecta a Elasticsearch y expone la interfaz gráfica en el puerto 5601.

```yaml
  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

### Jobmanager

El servicio jobmanager es el nodo maestro del sistema Apache Flink, responsable de coordinar la ejecución de trabajos de procesamiento de datos en tiempo real o por lotes. Asigna tareas a los TaskManagers, gestiona puntos de control y reinicios, y expone su interfaz de control en el puerto 8081.

```yaml
  jobmanager:
    image: flink:2.0.0-scala_2.12-java21 
    container_name: jobmanager
    ports:
      - "8081:8081"
    command: jobmanager
    volumes:
      - ./jars:/opt/flink/usrlib
    environment:
      - |
        FLINK_PROPERTIES=
        jobmanager.rpc.address: jobmanager
```

### Taskmanager

El servicio taskmanager ejecuta las tareas asignadas por el JobManager en Flink. Es responsable de realizar el procesamiento distribuido de los datos, gestionar la memoria y las redes locales, y comunicar resultados intermedios. En un clúster, se pueden escalar varios TaskManagers para distribuir la carga de trabajo.

```yaml
  taskmanager:
    image: flink:2.0.0-scala_2.12-java21
    container_name: taskmanager
    depends_on:
      - jobmanager
    command: taskmanager
    volumes:
      - ./jars:/opt/flink/usrlib
    environment:
      - |
        FLINK_PROPERTIES=
        jobmanager.rpc.address: jobmanager
        taskmanager.numberOfTaskSlots: 10
```

### SQL-client

El servicio sql-client permite ejecutar sentencias SQL sobre streams y tablas definidas en Flink. Es una herramienta interactiva que facilita el desarrollo, prueba y ejecución de consultas sin necesidad de escribir código Java o Scala. Se conecta al entorno de Flink y permite explorar en tiempo real los resultados de consultas sobre fuentes como Kafka, Elasticsearch o archivos.

```yaml
  sql-client:
    image: flink:2.0.0-scala_2.12
    container_name: sql-client
    tty: true
    stdin_open: true
    volumes:
      - ./jars:/opt/flink/usrlib
    depends_on:
      - jobmanager
      - kafka
      - elasticsearch
      - mariadb
    command: >
      bash -c "sleep 10 && ./bin/sql-client.sh"
    environment:
      FLINK_JOBMANAGER_HOST: jobmanager
      ZOOKEEPER_CONNECT: zookeeper
      KAFKA_BOOTSTRAP: kafka
      MYSQL_HOST: mariadb
      ES_HOST: elasticsearch
```

---

## Modo de uso

Vamos a explicar paso a paso como replicar este proyecto.

### 1. Clona el repositorio y accede al directorio del segundo proyecto:

```bash
git clone https://github.com/Wolfxyz16/ipmd-yeray2.git
cd ipmd-yeray2/trabajo-practico-3
```

### 2. Descarga de datos

En caso de no tener los datos con los que vamos a trabajar descargados

```bash
sh download-data.sh
```

### 2. Construir y arrancar el `docker-compose`

```bash
docker compose compose build
```

Lo arrancamos y lo ponemos en segundo plano.

```bash
docker compose compose up
```

Ahora podemos comprobar que los contendores están levantados con el siguiente comando

```bash
docker ps
```

Deberiamos ver los siguientes contenedores

![Captura de pantalla donde vemos los contenedores que están en funcionamiento]()

Debemos esperar unos segundos antes de continuar con la guia con el fin de que todos los contenedores arranquen correctamente, sobre todo la base de datos mariadb.

### 3. Crompobar que el contenedor generador esta generando los tweets

Una vez arrancados todos los contenedores debemos esperar para estar seguros de que el generador esta creando los datos 

```bash
docker logs -f generador
```
Sabremos que el script generador.py a iniciado correctamente cuando veamos los datos generados por terminal

![Captura de pantalla de una terminal donde se ven los tweets generados]()

### 4. Creamos las tablas 

Una vez tenemos el generador funcionando correctamente crearemos las tablas mediante sql-client

```bash
docker exec -it sql-client bash
```

Dentro del contenedor sql-client debemos acceder a flink para la creación de las tablas

```bash
./bin/sql-client.sh
```

Ahora que hemos accedido a flink

```bash
CREATE TABLE ktuits (
    user_id STRING,
    tweet STRING,
    proctime AS PROCTIME()
) WITH (
    'connector' = 'kafka',
    'topic' = 'ktuits',
    'properties.bootstrap.servers' = 'kafka:9092',
    'format' = 'json',
    'scan.startup.mode' = 'earliest-offset'
);
```

```bash
CREATE TABLE personalities (
    id BIGINT,
    mbti_personality STRING,
    pers_id TINYINT
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:mysql://mariadb:3306/ipmd',
    'table-name' = 'mbti_labels',
    'username' = 'wolfxyz',
    'password' = 'wolfxyz',
    'driver' = 'com.mysql.cj.jdbc.Driver'
);
```

```bash
CREATE TABLE count_per_personality (
    mbti_personality STRING,
    cnt BIGINT,
    pers_id TINYINT
) WITH (
    'connector' = 'elasticsearch-7',
    'hosts' = 'http://elasticsearch:9200',
    'index' = 'count_per_personality'
);
```

Si hemos realizado las acciones correctamente deberiamos ver las tablas en flink

![Captura de pantalla de una terminal donde vemos las tablas creadas en flink]()

### 5. TODO



### 6. Kibana

Para la creación de graficas en Kibana debemos acceder a su interfaz web desde un navegador. Así que vamos a ir a la dirección, 

#### [http://localhost:5601](http://localhost:5601)

TODO