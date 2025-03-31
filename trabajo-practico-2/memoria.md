# Trabajo práctico 1. Yeray Carretero y Yeray Li.

## Estructura del proyecto

```bash
├── README.md
├── config
├── memoria.md
├── requeriments.txt
├── docker-compose.yaml
├── db
│   └── init.sql
├── ejecutor
│   ├── Dockerfile
│   └── export_to_mariadb.py
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

* `docker-compose.yaml`: Orquesta todos los servicios (BD, Hive, Namenode, Datanodes, etc.) en contenedores.
* `requirements.txt`: Lista de dependencias de Python necesarias para la API (Flask, conectores MySQL, métricas, etc.).
* `config`: Configuración con la que se inicara el contenedor namenode.


* `db/init.sql`: Script SQL que inicializa la base de datos y crea las tablas necesarias. En este trabajo, las tablas creadas son para asegurar la implementación tanto de grafana como de superset

* `ejecutor/Dockerfile`:  Define la imagen de Docker para un contenedor de python, instalando dependencias y configurando su ejecución.
* `ejecutor/export_to_mariadb.py`:  Creamos conexiones con los contenedores de Hive y Mariadb para poder migrar los datos de Hive a una base de datos en Mariadb.

* `hive/Dockerfile`:  Define la imagen de Docker para un contenedor de Hive, instalando dependencias y configurando su ejecución.
* `hive/init_hive.sql`:  Crearemos las tablas necesarias para el trabajo, obteniendo los datos que han sido subidos a HDFS.

* `namenode/Dockerfile`:  Define la imagen de Docker para un contenedor de Hadoop, instalando dependencias y configurando su ejecución.
* `namenode/init_hdfs.sh`:  Se inicia el NameNode de HDFS, se crean directorios, se asignan permisos y se suben archivos `.avro` a HDFS.

* `estructura/`:  Carpeta que contiene la estructura de la base de datos que crearemos `userdata.avsc`.

* `userdata/`:  Carpeta que alamacena los datos de la base de datos en formato `.avro`.



### [`ejecutor/Dockerfile`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/ejecutor/Dockerfile) 

```Dockerfile
FROM python:3

WORKDIR /trabajo-practico-2

COPY requeriments.txt .
RUN pip install --no-cache-dir -r requeriments.txt

COPY ./ejecutor/export_to_mariadb.py ./export_to_mariadb.py

CMD [ "python", "./export_to_mariadb.py" ]

```

Dentro especificamos una imagen de la version 3 de python.

- Se hace una copia de `requeriments.txt` dentro del contenedor y se instalan las librerias que contiene dicho archivo.
- Copiamos el archivo `export_to_mariadb.py`.
- Mediante `CMD` una vez iniciado el contenedor se ejecuta el script.

### [`ejecutor/export_to_mariadb.py`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/ejecutor/export_to_mariadb.py) 

```python

TODO

```
TODO



### [`hive/Dockerfile`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/hive/Dockerfile) 

```Dockerfile
FROM apache/hive:3.1.3

# Establecer el directorio de trabajo
WORKDIR /trabajo-practico-2
USER root
# Asegurar permisos de root para instalar paquetes
RUN apt-get update && apt-get install -y python3-pip
# Copiar e instalar dependencias de Python
RUN mkdir -p /home/hive/.beeline && chown hive:hive /home/hive/.beeline
USER hive
# Copiar los scripts y datos
COPY hive/init_hive.sql init_hive.sql
COPY userdata /app/userdata 

# Ejecutar SQL en Hive y luego exportar a MariaDB
#CMD[beeline -u jdbc:hive2://localhost:10000/ -f hive/init_hive.sql && python3 hive/export_to_mariadb.py]

```

Dentro especificamos una imagen hive.

- Se instalan los paquetes necesarios para poder ejecutar el script `init_hive.sql`
- Se crea la carpeta `/home/hive/.beeline` para evitar errores en la ejecución.
- Copiamos el archivo `init_hive.sql`.
- Copiamos la carpeta `userdata` con los archivos `.avro`.

### [`hive/init_hive.sql`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/hive/init_hive.sql) 

```sql

-- Crear tabla externa con formato AVRO
CREATE EXTERNAL TABLE IF NOT EXISTS usuarios
STORED AS AVRO
LOCATION 'hdfs://namenode/user/hive/userdata'
TBLPROPERTIES ('avro.schema.url'='hdfs://namenode/user/hive/estructura/userdata.avsc');

-- Crear tabla resumen de usuarios por país
CREATE TABLE IF NOT EXISTS summary AS
SELECT country, COUNT(*) AS user_count
FROM usuarios
GROUP BY country
ORDER BY user_count DESC
LIMIT 10;

```
Este archivo nos sirve para una vez cargados los datos en HDFS podamos crear las tablas necesarias para la tarea mediante el contenedor de hive

- Se crea la `EXTERNAL TABLE usuarios` con la estructura `userdata.avsc` y con los datos `.avro`.
- Una vez creada la tabala `usuarios` creamos la tabla summary que contendra una pequeña proporción de los datos.


### [`namenode/Dockerfile`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/namenode/Dockerfile) 

```Dockerfile
FROM apache/hadoop:3

# Establecer el directorio de trabajo
WORKDIR /trabajo-practico-2

# Copiar los scripts necesarios
COPY /namenode/init_hdfs.sh init_hdfs.sh

# Ejecutar el script al iniciar el contenedor
CMD ["/bin/bash", "./init_hdfs.sh"]


```

Dentro especificamos una imagen hadoop.

- Copiamos el archivo `init_hdfs.sh`.
- Mediante `CMD` una vez iniciado el contedor ser ejecuta el script `init_hdfs.sh`.


### [`namenode/init_hdfs.sh`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/namenode/init_hdfs.sh) 

```sh

#!/bin/bash
hdfs namenode

echo "hola toy aqui"

# Crear y asignar permisos en HDFS
hdfs dfs -mkdir -p hdfs://namenode/user/hive
hdfs dfs -chown hive hdfs://namenode/user/hive
hdfs dfs -mkdir -p hdfs://namenode/user/hive/warehouse
hdfs dfs -chown hive hdfs://namenode/user/hive/warehouse
hdfs dfs -mkdir -p hdfs://namenode/home/hive
hdfs dfs -chown hive hdfs://namenode/home/hive

# Crear directorio en HDFS
hdfs dfs -mkdir -p hdfs://namenode/user/hive/userdata/
hdfs dfs -chown hive hdfs://namenode/user/hive/userdata/
hdfs dfs -mkdir -p hdfs://namenode/user/hive/estructura/
hdfs dfs -chown hive hdfs://namenode/user/hive/estructura/

# Subir archivos AVRO a HDFS
hdfs dfs -put /userdata/* hdfs://namenode/user/hive/userdata/
hdfs dfs -put /estructura/* hdfs://namenode/user/hive/estructura/

echo "✅ Datos AVRO cargados en HDFS correctamente."


```

Mediante este archivo, crearemos los directorios necesarios para el contenedor namenode.

- Mediante `mkdir` crearemos las carpetas necesarias dentro de hdfs, siempre y cuando la carpeta se cree dentro de `hdfs://namenode/`
- Con el comando `chown` diremos que hive sera el propietario de las carpetas creadas para que pueda acceder sin restricciones a ellas.
- Por ultimo cargamos tanto los datos como la estructura de estos dentro de sus carpetas correspondientes.


### [`config`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/config)

```
HADOOP_HOME=/opt/hadoop
CORE-SITE.XML_fs.default.name=hdfs://namenode
CORE-SITE.XML_fs.defaultFS=hdfs://namenode
HDFS-SITE.XML_dfs.namenode.rpc-address=namenode:8020
HDFS-SITE.XML_dfs.replication=1
ENSURE_NAMENODE_DIR=/tmp/hadoop-root/dfs/name

```

Declaramos la configuración del contenedor namenode para que realiza las conexciones correctamente.


## Servicios

Vamos a ir explicando los servicios a la vez que el bloque de código que los define en el archivo [`docker-compose.yaml`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-1/docker-compose.yaml).

Dentro de este archivo definimos los servicios que levantaremos luego con el comando `docker-compose up --build`. En nuestro caso, cada servicio esta asociado a un contenedor, excepto el servicio web que lo tenemos replicado con 4 copias. Por último, todos los servicios que tenemos estan dentro de la red llamada `trabajo1`.

### Web (flask)
En el servicio de web tenemos una simple API REST hecha con flask, un framework escrito en python. Esta es una API REST sencilla donde se implementa una base de datos con mensajes escritos, su id, y el contenedor donde se han creado.

```yaml
  web:
    build: .
    expose:
      - "5000"
    depends_on:
      - mariadb
    deploy:
      mode: replicated
      replicas: 4
    networks:
        - trabajo1
```

En el servicio web tenemos que expone el puerto 5000, depende del servicio mariadb, hasta que el servicio mariadb no este arrancado no se van crear los contenedores de web; en deploy especificamos cuántas veces queremos el contenedor replicado.

### Mariadb
En el servicio de Mariadb hay alojada un servidor mariadb que se encarga de almacenar toda la información. Cuando una instancia web recibe una petición REST, esta se comunica con el servidor para llevar a cabo la tarea. A la hora de crear el contenedor, montamos un volumen en el directorio `/docker-entrypoint-initdb.d/`. Dentro del volumen le pasamos un pequeño script sql para que el servidor ejecutará al iniciarse. Dentro del script creamos la base de datos, definimos las tablas, creamos los usuarios y definimos los permisos para que solo puedan acceder a la base de datos de la aplicación.

```yaml
  mariadb:
    image: mariadb
    container_name: "mariadb"
    restart: always
    ports:
      - "3306:3306"
    volumes:
      - ./db:/docker-entrypoint-initdb.d/:ro
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_USER: wolfxyz
      MYSQL_PASSWORD: wolfxyz
      MYSQL_DATABASE: ipmd
    networks:
      - trabajo1
```

El servicio mariadb contiene el servidor donde se ejecuta el SGBD mariadb. Indicamos la imagen de mariadb, definimos el nombre y que cuando el servicio se caiga o docker se detenga (`restart: always`). En la línea de puerto mapeamos el puerto 3306 con el puerto 3306 de nuestro ordenador. En volumenes le indicamos el directorio  `./db` de nuestro repositorio, en el encontramos un script que el servidor ejecutará cada vez que se inicie.

En la línea de `environment` le indicamos al contenedor las variables de entorno que tiene que tener sus sistema operativo. En nuestro caso nos ayudan a pre-configurar el servidor mariadb.

### Adminer
El servicio de Adminer consiste en una interfaz web donde podemos acceder a la base de datos de mariadb. Sinceramente solo lo hemos usado para comprobar que la base de datos ha ejecutado el archivo de inicialización.

```yaml
adminer:
    image: adminer
    container_name: "adminer"
    restart: always
    ports:
      - "8080:8080"
    environment:
      ADMINER_DEFAULT_SERVER: mariadb
    networks:
      - trabajo1
```

### mysqld-exporter
El servicio de mysqld-exporter actúa como un adaptador que extrae métricas internas de MariaDB y las convierte en un formato compatible con Prometheus. Este servicio se encarga de recopilar información clave sobre el rendimiento de la base de datos, como el uso de conexiones, el tiempo de respuesta de las consultas, el consumo de recursos y el estado de los índices. Luego, expone estas métricas a través de un endpoint HTTP accesible por Prometheus, permitiendo su almacenamiento y análisis en tiempo real.

```yaml
mysqld-exporter:
      image: quay.io/prometheus/mysqld-exporter
      container_name: "mysqld-exporter"
      restart: always
      ports:
        - "9104:9104"
      command:
        - "--config.my-cnf=/etc/.my.cnf"
        - "--mysqld.address=mariadb:3306"
      volumes:
        - ./config.my-cnf:/etc/.my.cnf
      extra_hosts:
        - "mysqld-exporter:127.0.0.1"
      networks:
        - trabajo1
```

### Prometheus
El servicio de Prometheus es una herramienta open-source para la gestión de
datos de monitorización de aplicaciones y servicios. Mediante este servicio extraerán las métricas almacenadas en el servicio de mysqld-exporter. Aunque este, sí que nos permite visualizar métricas de manera intuitiva, prometheus actuará como datasource Grafana.

```yaml
prometheus:
    image: prom/prometheus
    container_name: "prometheus"
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - trabajo1
```

### Grafana
Grafana es una herramienta open-source para visualizar series temporales en una interfaz WebUI. Mediante Grafana se nos permite crear dashboards interactivos y personalizables para monitorear el estado y rendimiento de aplicaciones, bases de datos y servidores en tiempo real. 
Para obtener los datos Grafana necesita de un datasource el cual almacenará y proporcionará los datos en tiempo (Prometheus).

```yaml
grafana:
    image: grafana/grafana
    container_name: "grafana"
    restart: always
    ports:
      - "3000:3000"
    networks:
       - trabajo1
    volumes:
      - grafana-storage:/var/lib/grafana
```

### Nginx
El servicio de nginx contiene un servidor web nginx. En nuestro caso usamos este contenedor como balanceador de carga ya que tenemos el servicio web con replicación. Este es otro servicio que ha sido relativamente fácil de implementar ya que solo tenemos que indicar en el archivo de configuración el nombre del servicio y el puerto.

```yaml
nginx:
    image: nginx:latest
    container_name: "nginx"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
    depends_on:
      - web
    networks:
      - trabajo1
```

## Modo de uso
1. Clona el repositorio:
    ```bash
    git clone https://github.com/Wolfxyz16/ipmd-yeray2.git
    ```
2. Navega al directorio del proyecto:
    ```bash
    cd ipmd-yeray2/trabajo-practico-1
    ```
3. Ejecutar docker compose
    ```bash
    docker compose up -d
    ```

    * Comprobamos que los contenedores esten levantados
    ```bash
    docker ps
    ```

    ![Captura de pantalla donde vemos los contenedores que están en funcionamiento](imagenes/Docker_ps.png)

    * Comprobamos que el servicio web+nginx esté en funcionamiento
    ```bash
    curl -X GET http://localhost:80/data
    ```

    ![Captura de pantalla del servicio web en funcionamiento](imagenes/replicacion.png)

    * Comprobamos que el servicio web está conectado con la base de datos

    ![Captura de pantalla donde vemos que la base de datos se actualiza](imagenes/insertar_borrar.png)

4. Acceder a los servicios:
    ```bash
    API Flask + nginx: http://localhost:80

    Adminer: http://localhost:8080

    Prometheus: http://localhost:9090

    Grafana: http://localhost:3000
    ```

    * Podemos comprobar también que la aplicación tiene los errores controlados:

    ![Captura de pantalla de una interfaz de comandos](imagenes/controlError_get.png)

    ![Captura de pantalla de una interfaz de comandos](imagenes/controlError_post.png)

    ![Captura de pantalla de una interfaz de comandos](imagenes/controlError_delete.png)

5. Prometheus

    Si entramos en [http://localhost:9090](http://localhost:9090) podemos ver los servicios que monitorea prometheus.

    ![Captura de pantalla con los targets de prometheus](imagenes/Prometheus.png)

6. Paneles de grafana

     ```bash
    Panel para MySQL Exporter: código 14057 de la biblioteca de paneles de Grafana
    Panel para aplicaciones Flask: se facilita en formato JSON
    Panel extra para mariadb utiles : código 13106 de la biblioteca de paneles de Grafana
    ```

    ![Código json proporcionado en egela](imagenes/grafana_json.png)

    ![Panel para mysql exporter](imagenes/grafana_sql.png)
