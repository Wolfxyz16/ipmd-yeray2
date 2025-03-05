# Trabajo práctico 1. Yeray Carretero y Yeray Li.

## Estructura del proyecto

```bash
├── app.py
├── config.my-cnf
├── db
│   └── init.sql
├── docker-compose.yaml
├── Dockerfile
├── memoria.md
├── nginx.conf
├── prometheus.yml
├── README.md
└── requirements.txt
```

* `Dockerfile`:  Define la imagen de Docker para la API Flask, instalando dependencias y configurando su ejecución.
* `app.py`: Código fuente de la API REST en Flask, que gestiona operaciones sobre la base de datos.
* `config.my-cnf`: Archivo de configuración para MySQL/MariaDB, estableciendo parámetros como credenciales y rendimiento.
* `db/init.sql`: Script SQL que inicializa la base de datos y crea las tablas necesarias.
* `docker-compose.yaml`: Orquesta todos los servicios (API, BD, Adminer, Prometheus, Grafana, etc.) en contenedores.
* `nginx.conf`: Configuración de Nginx como balanceador de carga para distribuir tráfico entre instancias de la API.
* `prometheus.yml`: Configuración de Prometheus para recolectar métricas de los servicios en ejecución.
* `requirements.txt`: Lista de dependencias de Python necesarias para la API (Flask, conectores MySQL, métricas, etc.).

### `Dockerfile`

```Dockerfile
FROM python:3.10-alpine
WORKDIR /app
ENV FLASK_APP=app.py
RUN apk add --no-cache gcc musl-dev linux-headers mysql-client
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
```

Dentro 

## Servicios

> [!IMPORTANT]
> Tenemos que explicar como entrar a grafana y a mariadb. Explicar todo un poco mas en general

### Web (flask)
En el servicio de web tenemos una simple API REST hecha con flask, un framework escrito en python. Esta es una API REST sencilla donde se implementa una base de datos con mensajes escritos, su id, y el contenedor donde se han creado.

### Mariadb
En el servicio de Mariadb hay alojada un servidor mariadb que se encarga de almacenar toda la información. Cuando una instancia web recibe una petición REST, esta se comunica con el servidor para llevar a cabo la tarea. A la hora de crear el contenedor, montamos un volumen en el directorio `/docker-entrypoint-initdb.d/`. Dentro del volumen le pasamos un pequeño script sql para que el servidor ejecutará al iniciarse. Dentro del script creamos la base de datos, definimos las tablas, creamos los usuarios y definimos los permisos para que solo puedan acceder a la base de datos de la aplicación.

### Adminer
El servicio de Adminer consiste en una interfaz web donde podemos acceder a la base de datos de mariadb. Sinceramente solo lo hemos usado para comprobar que la base de datos ha ejecutado el archivo de inicialización.

### mysqld-exporter
El servicio de mysqld-exporter actúa como un adaptador que extrae métricas internas de MariaDB y las convierte en un formato compatible con Prometheus. Este servicio se encarga de recopilar información clave sobre el rendimiento de la base de datos, como el uso de conexiones, el tiempo de respuesta de las consultas, el consumo de recursos y el estado de los índices. Luego, expone estas métricas a través de un endpoint HTTP accesible por Prometheus, permitiendo su almacenamiento y análisis en tiempo real.

### Prometheus
El servicio de Prometheus es una herramienta open-source para la gestión de
datos de monitorización de aplicaciones y servicios. Mediante este servicio extraerán las métricas almacenadas en el servicio de mysqld-exporter. Aunque este, sí que nos permite visualizar métricas de manera intuitiva, prometheus actuará como datasource Grafana.

### Grafana
Grafana es una herramienta open-source para visualizar series temporales en una interfaz WebUI. Mediante Grafana se nos permite crear dashboards interactivos y personalizables para monitorear el estado y rendimiento de aplicaciones, bases de datos y servidores en tiempo real. 
Para obtener los datos Grafana necesita de un datasource el cual almacenará y proporcionará los datos en tiempo (Prometheus).

### Nginx
El servicio de nginx contiene un servidor web nginx. En nuestro caso usamos este contenedor como balanceador de carga ya que tenemos el servicio web con replicación. Este es otro servicio que ha sido relativamente fácil de implementar ya que solo tenemos que indicar en el archivo de configuración el nombre del servicio y el puerto.

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
4. Acceder a los servicios:
    ```bash
    API Flask + nginx: http://localhost:80

    Adminer: http://localhost:8080

    Prometheus: http://localhost:9090

    Grafana: http://localhost:3000
    ```
5. Paneles de grafana
     ```bash
    Panel para MySQL Exporter: código 14057 de la biblioteca de paneles de Grafana
    Panel para aplicaciones Flask: se facilita en formato JSON
    Panel extra para mariadb utiles : código 13106 de la biblioteca de paneles de Grafana
    ```
