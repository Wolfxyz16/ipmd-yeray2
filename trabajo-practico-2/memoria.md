# Trabajo práctico 2. Yeray Carretero y Yeray Li.

## Estructura del proyecto

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

* `docker-compose.yaml`: Orquesta todos los servicios (BD, Hive, Namenode, Datanodes, etc.) en contenedores.
* `config`: Configuración con la que se inicara el contenedor namenode y datanode.


* `db/init.sql`: Script SQL que inicializa la base de datos y crea las tablas necesarias. En este trabajo, las tablas creadas son para asegurar la implementación tanto de grafana como de superset

* `ejecutor/init.sh`: Script para la ejecución del contenedor que va a copiar los datos desde hive a mariadb.
* `ejecutor/Dockerfile`:  Define la imagen de Docker para un contenedor de python, instalando dependencias y configurando su ejecución.
* `ejecutor/export_to_mariadb.py`:  Creamos conexiones con los contenedores de Hive y Mariadb para poder migrar los datos de Hive a una base de datos en Mariadb.
* `ejecutor/requeriments.txt`: Lista de dependencias de python necesarias para ejecutar el contenedor.

* `hive/Dockerfile`:  Define la imagen de Docker para un contenedor de Hive, instalando dependencias y configurando su ejecución.
* `hive/init_hive.sql`:  Crearemos las tablas necesarias para el trabajo, obteniendo los datos que han sido subidos a HDFS.

* `namenode/Dockerfile`:  Define la imagen de Docker para un contenedor de Hadoop, instalando dependencias y configurando su ejecución.
* `namenode/init_hdfs.sh`:  Se inicia el NameNode de HDFS, se crean directorios, se asignan permisos y se suben archivos `.avro` a HDFS.

* `estructura/`:  Carpeta que contiene la estructura de la base de datos que crearemos `userdata.avsc`.
* `userdata/`:  Carpeta que alamacena los datos de la base de datos en formato `.avro`.

Ahora vamos a explicar que hace cada servicio que se detallada en el archivo `docker-compose.yaml` y los archivos que lo componen.

## Servicio «ejecutor»

Técnicamente no es un servicio ya que lo ejecutamos manualmente una vez que hive ya tiene datos. Este contenedor se encarga de pasar los datos que tenemos en hive a una tabla en nuestro servicio mariadb. Consiste en una imagen `python:3` que ejecuta un script que hemos programado. 

### [`ejecutor/Dockerfile`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/ejecutor/Dockerfile) 

Imagen del contendor.

```Dockerfile
FROM python:3

WORKDIR /trabajo-practico-2

COPY requeriments.txt .
RUN pip install --no-cache-dir -r requeriments.txt

COPY ./export_to_mariadb.py ./export_to_mariadb.py
RUN chmod +x export_to_mariadb.py

CMD [ "python", "./export_to_mariadb.py" ]
```

### [`ejecutor/init.sh`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/ejecutor/init.sh)

Script que construye la imagen, lanza el contenedor y por último elimina la imágen.

```sh
#!/usr/bin/env bash
cd "$(dirname "$0")"

docker build -t ejecutor ../ejecutor
docker run --name=ejecutor --network=mynet ejecutor

# habría que comprobar que el comando se llega a ejecutar
docker stop ejecutor
docker rm ejecutor
docker image rm ejecutor
```

### [`ejecutor/export_to_mariadb.py`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/ejecutor/export_to_mariadb.py) 

Consiste en crear dos conexiones, una a mariadb y la otra a hive. Una vez las conexiones son correctas copiamos los datos dentro de la tabla `summary` de mariadb. Tenemos que ejecutarlo cuando hive ya tenga los datos cargados y cuando nos aseguremos de que mariadb se está ejecutando.

## Servicio Hive

### [`hive/Dockerfile`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/hive/Dockerfile) 

Hive nos permite almacenar los datos y poder consultarlos usando sentencias SQL. Esta es la imágen de Docker con el que lo definimos. Usamos la imágen oficial de `apache/hive:4.0.0` y luego le añadimos los el script de inicialización y los datos.

```Dockerfile
FROM apache/hive:4.0.0

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

# # Añadimos los archivos de configuracion
# ADD hive/hive-site.xml /opt/hive/conf/hive-site.xml

# Ejecutar SQL en Hive y luego exportar a MariaDB
CMD [beeline -u jdbc:hive2://localhost:10000/ -f hive/init_hive.sql]
```

### [`hive/init_hive.sql`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/hive/init_hive.sql) 

En el script de inicialización de hive le indicamos que cree una tabla usando los datos que encuentre en el directorio de `hdfs`. Debemos especificarle también la estructura que se encuentra en otro directorio de `hdfs`.

Una vez lo tenemos creamos una tabla en hive llamada summary que cuenta cuántos usuarios hay por cada país. Esta es la tabla que vamos a exportar luego a mariadb con el contenedor `ejecutor`.

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

## Servicio HDFS, namenode y datanode.

El almacenamiento en HDFS nos permite guardar grandes volúmenes de datos y está dividido en dos servicios diferentes, el namenode y el datanode.

El namenode es el componente encargado de gestionar la estructura de directorios y la metadata de los archivos en HDFS. Almacena información sobre qué bloques de datos están almacenados en qué datanode. No guarda los datos reales, solo las ubicaciones de los bloques. Si el namenode falla, puede comprometer la integridad del sistema.

El datanode son los encargados de almacenar físicamente los bloques de datos. Cada datanode gestiona los datos que le asignan y realiza operaciones de lectura y escritura según las peticiones del cliente. Además, envían información sobre el estado de los bloques al namenode para asegurar la consistencia y la replicación adecuada de los datos.

La elección de imágenes han sido las oficiales de `apache/hadoop:3` que cuentan con la versión más actualizada. Dentro del archivo `yaml` le indicamos a cada servicio con qué comando tiene que arrancar.

Para los datanodes (en nuestro caso dos), no necesitamos un archivo `Dockerfile`. Sin embargo, para el namenode, sí lo necesitamos. En él vamos a copiar el script que se encargará de crear la estructura de datos (los directorios) con los que vamos a trabajar.

### [`namenode/Dockerfile`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/namenode/Dockerfile) 

Este es el `Dockerfile` que usaremos para especificar al namenode.

```Dockerfile
FROM apache/hadoop:3

# Establecer el directorio de trabajo
WORKDIR /trabajo-practico-2

# Copiar los scripts necesarios
COPY /namenode/init_hdfs.sh init_hdfs.sh

# Ejecutar el script al iniciar el contenedor
CMD ["/bin/bash", "./init_hdfs.sh"]
```

### [`namenode/init_hdfs.sh`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/namenode/init_hdfs.sh) 

Mediante este archivo, crearemos los directorios necesarios para el contenedor namenode.

- Mediante `mkdir` crearemos las carpetas necesarias dentro de hdfs, siempre y cuando la carpeta se cree dentro de `hdfs://namenode/`
- Con el comando `chown` diremos que hive sera el propietario de las carpetas creadas para que pueda acceder sin restricciones a ellas.
- Por ultimo cargamos tanto los datos como la estructura de estos dentro de sus carpetas correspondientes.

```sh
#!/bin/bash
echo "Creating hdfs project structure..."

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

echo "Uploading data to hdfs..."

# Subir archivos AVRO a HDFS
hdfs dfs -put /userdata/* hdfs://namenode/user/hive/userdata/
hdfs dfs -put /estructura/* hdfs://namenode/user/hive/estructura/

echo "✅ Datos AVRO cargados en HDFS correctamente."
```

### [`config`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/config)

Declaramos la configuración del contenedor namenode para que realiza las conexciones correctamente.

```
HADOOP_HOME=/opt/hadoop
CORE-SITE.XML_fs.default.name=hdfs://namenode
CORE-SITE.XML_fs.defaultFS=hdfs://namenode
HDFS-SITE.XML_dfs.namenode.rpc-address=namenode:8020
HDFS-SITE.XML_dfs.replication=1
ENSURE_NAMENODE_DIR=/tmp/hadoop-root/dfs/name
```

## Servicio mariadb

### [`init.sql`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/db/init.sql)

En este archivo creamos los usuarios por defecto, damos privilegios y creamos la tabla `summary`.

```sql
-- Creamos los usuarios
CREATE USER IF NOT EXISTS 'wolfxyz'@'%' IDENTIFIED BY 'wolfxyz';
CREATE USER IF NOT EXISTS 'grafana'@'%' IDENTIFIED BY 'grafana';

-- Creamos la base de datos
CREATE DATABASE IF NOT EXISTS ipmd;

-- Creamos la tabla summary
CREATE TABLE IF NOT EXISTS ipmd.summary (
    country VARCHAR(255) PRIMARY KEY,
    user_count INT NOT NULL
);

-- Damos privilegios a los usuarios
GRANT ALL PRIVILEGES ON ipmd TO 'wolfxyz'@'%';
GRANT SELECT ON ipmd TO 'grafana'@'%';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'wolfxyz'@'%';
GRANT SLAVE MONITOR ON *.* TO 'wolfxyz'@'%';
GRANT REPLICATION CLIENT ON *.* TO 'wolfxyz'@'%';

-- Aplicamos los privilegios
FLUSH PRIVILEGES;
```

## [`docker-compose.yaml`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/docker-compose.yaml)

Vamos a ir explicando la especificación de cada servicio en el archivo [`docker-compose.yaml`](https://github.com/Wolfxyz16/ipmd-yeray2/blob/main/trabajo-practico-2/docker-compose.yaml).

Dentro de este archivo definimos los servicios que levantaremos luego con el comando `docker-compose up --build`. Para este trabajo, todos los servicios que tenemos estan dentro de la red llamada `mynet`.

### Namenode

El servicio namenode es el nodo maestro del sistema de archivos distribuido HDFS. Su función principal es gestionar la metadata del sistema de archivos, es decir, el seguimiento de qué archivos existen y en qué nodos de datos están almacenados los bloques de cada archivo.

```yaml
  namenode:
    # image: apache/hadoop:3
    build:
      context: .
      dockerfile: namenode/Dockerfile
    hostname: namenode
    container_name: namenode
    ports:
      - 9870:9870
    command: ["hdfs", "namenode"]
    env_file:
      - ./config
    volumes:
      - ./userdata:/userdata
      - ./estructura:/estructura
    environment:
      ENSURE_NAMENODE_DIR: "/tmp/hadoop-root/dfs/name"
    networks:
      mynet:
        ipv4_address: 172.18.0.2
```

### Datanode 1-2

Los datanode son los nodos de almacenamiento dentro del sistema HDFS. Su función es almacenar físicamente los bloques de datos y responder a las solicitudes de lectura y escritura que provienen del namenode o de otros procesos dentro del clúster. Para este trabajo hemos definido dos datanode, lo que nos permite la replicación de datos y la tolerancia a fallos dentro del sistema distribuido. Con la línea `command` le indicamos que comando queremos ejecutar cuando arranque el contendor.

```yaml
  datanode_1:
    image: apache/hadoop:3
    container_name: datanode-1
    command: [ "hdfs", "datanode" ]
    env_file:
      - ./config
    networks:
      - mynet

  datanode_2:
    image: apache/hadoop:3
    container_name: datanode-2
    command: [ "hdfs", "datanode" ]
    env_file:
      - ./config
    networks:
      - mynet
```

### Hive

Apache Hive es un sistema de almacenamiento y análisis de datos basado en Hadoop. Este servicio proporciona una interfaz SQL para consultar y gestionar datos dentro del sistema HDFS. Hive facilita el procesamiento de grandes volúmenes de datos utilizando consultas similares a SQL. Debemos mapear los puertos de hive ya que querremos acceder desde nuestro ordenador a la interfaz web. También es necesaria la opción `depends_on` ya que hive debe esperar a que HDFS arranque antes de poder empezar.

```yaml
  hive:
    build:
      context: .
      dockerfile: hive/Dockerfile
    container_name: hive-server
    environment:
      - SERVICE_NAME=hiveserver2
    depends_on:
      - namenode
    ports:
      - "10000:10000"
      - "10002:10002"
    volumes:
      - ./hive:/hive
    networks:
      - mynet
```

### Superset

Apache Superset es una plataforma de visualización de datos que permite crear dashboards interactivos para analizar la información almacenada en bases de datos y sistemas distribuidos como Hive o MariaDB. Este servicio proporciona una interfaz gráfica en la que se pueden crear gráficos, tablas y reportes basados en las consultas realizadas sobre las fuentes de datos conectadas. 

```yaml
  superset:
    image: acpmialj/ipmd:ssuperset
    container_name: superset
    restart: always
    ports:
      - "8088:8088"
    environment: 
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_SECURITY_ADMIN_USER=admin
    networks:
      - mynet
```

### Mariadb

En el servicio de Mariadb hay alojada un servidor mariadb que se encarga de almacenar toda la información. Cuando una instancia web recibe una petición REST, esta se comunica con el servidor para llevar a cabo la tarea. A la hora de crear el contenedor, montamos un volumen en el directorio `/docker-entrypoint-initdb.d/`. Dentro del volumen le pasamos un pequeño script sql para que el servidor ejecutará al iniciarse. Dentro del script creamos la base de datos, definimos las tablas, creamos los usuarios y definimos los permisos para que solo puedan acceder a la base de datos de la aplicación.

```yaml
  mariadb:
    image: mariadb
    container_name: mariadb
    restart: always
    ports:
      - "3306:3306"
    volumes:
      - mariadb_data:/var/lib/mysql  
      - ./db:/docker-entrypoint-initdb.d/:ro
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_USER: wolfxyz
      MYSQL_PASSWORD: wolfxyz
      MYSQL_DATABASE: ipmd
    networks:
      - mynet
```

El servicio mariadb contiene el servidor donde se ejecuta el SGBD mariadb. Indicamos la imagen de mariadb, definimos el nombre y que cuando el servicio se caiga o docker se detenga (`restart: always`). En la línea de puerto mapeamos el puerto 3306 con el puerto 3306 de nuestro ordenador. En volumenes le indicamos el directorio  `./db` de nuestro repositorio, en el encontramos un script que el servidor ejecutará cada vez que se inicie.

En la línea de `environment` le indicamos al contenedor las variables de entorno que tiene que tener sus sistema operativo. En nuestro caso nos ayudan a pre-configurar el servidor mariadb.

### Grafana

Grafana es una herramienta open-source para visualizar series temporales en una interfaz WebUI. Mediante Grafana se nos permite crear dashboards interactivos y personalizables para monitorear el estado y rendimiento de aplicaciones, bases de datos y servidores en tiempo real. 

```yaml
grafana:
    image: grafana/grafana
    container_name: grafana
    restart: always
    ports:
      - "3000:3000"
    volumes:
      - grafana-storage:/var/lib/grafana  
    networks:
      - mynet
```

---

## Modo de uso

Vamos a explicar paso a paso como replicar este proyecto.

### 1. Clona el repositorio y accede al directorio del segundo proyecto:

```bash
git clone https://github.com/Wolfxyz16/ipmd-yeray2.git
cd ipmd-yeray2/trabajo-practico-2
```

### 2. Construir y arrancar el `docker-compose`

```bash
docker compose compose build
```

Lo arrancamos y lo ponemos en segundo plano.

```bash
docker compose compose build
```

Ahora podemos comprobar que los contendores están levantados con el siguiente comando

```bash
docker ps
```

Deberiamos ver los siguientes contenedores

![Captura de pantalla donde vemos los contenedores que están en funcionamiento](img/docker-ps.png)

Debemos esperar unos segundos antes de continuar con la guia con el fin de que todos los contenedores arranquen correctamente, sobre todo la base de datos mariadb.

### 3. Crear la estructura HDFS

Ejecutamos el archivo `./init_hdfs.sh` para iniciar correctamente la configuración de namenode y cargar los archivos correctamente en hive:

```bash
docker exec -it namenode ./init_hdfs.sh
```

Comprobamos que se ha ejecutado correctamente

```bash
docker exec -it datanode-1 hdfs dfs -ls hdfs://namenode/user/hive/userdata
docker exec -it datanode-1 hdfs dfs -ls hdfs://namenode/user/hive/estructura
```

![Captura de pantalla de una terminal donde se ven el resultado de los dos comandos anteriores](img/hdfs.png)

### 4. Creamos el servidor hive

Una vez los datos estan añadidos correctamente nos metemos en el contendor de hive y ejecutamos el `init_hive.sql`:

```bash
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000/ -f ./init_hive.sql
```

Tardará unos 10 segundos pero debemos ver que el status es `SUCCEEDED`. Una vez tenemos el servidor hive vamos a ejecutar un comando para comprobar que las tablas se han creado en hive correctamente

```bash
docker exec hive-server beeline -u jdbc:hive2://localhost:10000/ -e !tables
```

El resultado que debemos ver es algo parecido a esto:

![Captura de pantalla de una terminal donde vemos las tablas creadas en hive](img/hive-tables.png)

### 5. Llenar la base de datos, mariadb

El siguiente paso a realizar será pasar la información de las tablas que contiene hive a nuestro servidor mariadb que tenemos desplegado en un contendor. Para ello usaremos un *script* que es encuentra en la carpeta `ejecutor`. Ejecutamos el *script* `init.sh`:

```bash
./ejecutor/init.sh
```

Cuando termine el script vamos a ejecutar la siguiente consulta para comprobar que la tabla se ha llenado correctamente.

```bash
docker exec mariadb mariadb --user=wolfxyz --password=wolfxyz --table ipmd -e "SELECT * FROM summary"
```

![Captura de pantalla de una terminal donde vemos el resultado de la consulta a la base de datos mariadb](img/mariadb.png)

### 6. Grafana

Para la creación de Grafana debemos acceder a su interfaz web desde un navegador. Así que vamos a ir a la dirección, 

#### [http://localhost:3000/login](http://localhost:3000/login)

Primero debemos iniciar sesión. Las credenciales son wolfxyz wolfxyz.

![Captura de pantalla del inicio de sesión de grafana. Las credenciales son wolfxyz wolfxyz](img/grafana-login.png)

Dentro del panel principal debemos de ir al menu y buscar la opción *Add new connection*.

![Menu de opciones de grafana](img/grafana-menu.png)

Entramos y dentro nos saldrán una lista de diferentes *datasources*. El *datasource* debe de ser de tipo MySQL. Lo seleccionamos y luego en *Add new data source*.

Debemos especificar que el nombre del *data source* sea **mariadb**. La conexión al host dentrá la dirección `172.18.0.10`. El nombre de la base de datos será `ipmd`. Por último sus credenciales serán wolfxyz wolfxyz.

![Captura de pantalla donde se ven las opciones de los data sources](img/grafana-datasource.png)

Seleccionamos la opción al final de la página que dice *Save & test*, y deberiamos ver un cuadrado verde que nos indique que la conexión ha sido exitosa.

Ahora en el menú de grafana seleccionaremos la opción **Dashboards** y dentro la opción de crear un nuevos **Dashboard**.

Dentro de este menú, nos aparecerán tres opciones diferentes. Nosotros debemos seleccionar la que dice **+ Add visualization**.

![Captura de pantalla donde vemos la opcion de grafana que añadir una visualización](img/grafana-dahsboard1.png)

Ahora debemos seleccionar el *data source* que habiamos creado antes.

![Captura de pantalla donde vemos el data source de antes](img/grafana-dashboard2.png)

En este menú de creación de dashboards debemos ahora de seleccionar que tipo de gráfico queremos. A la izquierda del menú tenemos seleccionada la opción de **time-series**. Debemos quitarla y poner **Pie Chart**. Además en la opción de **Value options - show** debemos indicarle **All values**. Tambíen podemos cambiarle el nombre a **summary chart** para hacerlo mas profesional.

![Captura de pantalla del menú de creación de gráficas de grafana donde le indicamos que tiene que ser de tipo circular y que tome todos los valores.](img/grafana-dashboard3.png)

Ahora debemos indicarle que tabla queremos supervisar. Dentro de las opciones de *query* pulsamos en **Code** y añadimos lo siguiente:

```sql
SELECT * FROM ipmd.summary LIMIT 50 
```

![Captura de pantalla donde se muestra el comando sql que va a interpretar grafana](img/grafana-dashboard4.png)

Ahora deberiamos ver un gráfico parecido a este donde cada color represanta a un país:

![Captura de pantalla donde vemos el gráfico de circulos final de grafana](img/grafana-dashboard5.png)

### 7. Panele de superset

Superset nos permite también visualizar la tabla summary como alternativa a Grafana.

El primer paso será el inicio de sesión donde las credenciales vuelven a ser wolfxyz wolfxyz.

![Captura de pantalla de Superset y de su inicio de sesión](img/superset1.png)

Dentro del **+** que tenemos arriba a la derecha debemos seleccionar la opción *Data > Connect to database*.

Rellenamos el formulario con las siguientes opciones:

* host: 172.18.0.10
* port: 3306
* database name: ipmd
* username: wolfxyz
* password: wolfxyz
* display name: Mariadb

![Captura de pantalla de la creación de la conexión con la base de datos](img/superset2.png)

Ahora pulsamos en *create dataset* y pasamos a la siguiente pantalla.

Dentro del menú de creación de un nuevo *dataset* añadimos las siguiente opciones. La base de datos será la que hemos llamado **Mariadb**, el *schema* será ipmd y la tabla será *summary*. Pulsamos en *Create dataset and create chart*.

![Captura de pantalla de la creación del dataset](img/superset3.png)

Ahora en la barra superior de navegación debemos ir a la opción de **Charts**. Allí nos saldrá una opción con el icono de importar los *charts*. Podemos seleccionar los dos *charts.zip* que tenemos ya creados previamente y que se encuentran en la carpeta de `superset/`

![Captura de pantalla con el procesor de importación de un chart](img/superset4.png)

Ahora solo nos queda visualizar los resultados de estos dos *charts* diferentes. Tenemos uno de tipo *pie* muy parecido al de Grafana y otro de tipo mapamundi donde podemos ver las métricas en un mapa global agrupadas por paises.

![Captura de pantalla del chart de tipo pie](img/summary-pie.jpg)

![Captura de pantalla del chart de tipo country](img/summary-country.jpg)

### 8. The end (?)

Al terminar debemos parar y eliminar todos los contenedores que hemos creado con el siguiente comando:

```bash
docker compose down --volumes --remove-orphans
```
