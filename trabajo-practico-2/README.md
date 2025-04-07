# Procesamiento con Hive y visualización con Grafana

> [!Note]
> DEADLINE -> 9 de abril / 23:59

## Pasos a seguir

### Empezar los servicios

Construimos el archivo `docker compose`.

```bash
docker compose build
```

Lo arrancamos y lo ponemos en segundo plano.

```bash
docker compose up --detach
```

Debemos esperar unos segundos antes de continuar con la guia con el fin de que todos los contenedores arranquen correctamente, sobre todo la base de datos mariadb.

### Crear la estructura hdfs

Ejecutamos el archivo ./init_hdfs.sh para iniciar correctamente la configuración de namenode y cargar los archivos correctamente en hive

```bash
docker exec -it namenode ./init_hdfs.sh
```

Comprobamos que se ha ejecutado correctamente

```bash
docker exec -it datanode-1 hdfs dfs -ls hdfs://namenode/user/hive/userdata
docker exec -it datanode-1 hdfs dfs -ls hdfs://namenode/user/hive/estructura
```

### Crear hive-server

Una vez los datos estan añadidos correctamente nos metemos en el contendor de hive y ejecutamos el `init_hive.sql`:

```bash
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000/ -f ./init_hive.sql
```

Una vez tenemos el servidor hive vamos a ejecutar un comando para comprobar que las tablas se han creado en hive correctamente

```bash
docker exec hive-server beeline -u jdbc:hive2://localhost:10000/ -e !tables
```

### Llenar la base de datos, mariadb

El siguiente paso a realizar será pasar la información de las tablas que contiene hive a nuestro servidor mariadb que tenemos desplegado en un contendor. Para ello usaremos un *script* que es encuentra en la carpeta `ejecutor`. Ejecutamos el *script* `init.sh`:

```bash
./ejecutor/init.sh
```

Cuando termine el script vamos a ejecutar la siguiente consulta para comprobar que la tabla se ha llenado correctamente.

```bash
docker exec mariadb mariadb --user=wolfxyz --password=wolfxyz --table ipmd -e "SELECT * FROM summary"
```

### Grafana
[TODO]

### End

Al terminar debemos parar y eliminar todos los contenedores que hemos creado con el siguiente comando:

```bash
docker compose down --volumes --remove-orphans
```
