# Procesamiento con Hive y visualización con Grafana

> [!Note]
> DEADLINE -> 9 de abril / 23:59

WIP

**Falta hacer que la conexion entre hive y namenode vaya, si va si que se hace todo bien, pero hay que hacerlo de momento manualmente porque la ip cambian y ns que hacer **

**Pasos a seguir**
Terminal 1
''' bash
docker compose up --build
''' 
Terminal 2
'''
Ejecutamos el archivo ./init_hdfs.sh para iniciar correctamente la configuración de namenode y cargar los archivos correctamente en hive
docker exec -it namenode ./init_hdfs.sh

Comprobamos que se ha ejecutado correctamente
docker exec -it datanode-1 hdfs dfs -ls hdfs://namenode/user/hive/userdata
docker exec -it datanode-1 hdfs dfs -ls hdfs://namenode/user/hive/estructura


Una vez los datos estan añadidos correctamente nos metemos en el contendor de hive y ejecutamos el init_hive.sql
 docker exec -it hive-server bash

 beeline -u jdbc:hive2://localhost:10000/ 

 CREATE EXTERNAL TABLE IF NOT EXISTS usuarios
 STORED AS AVRO
 LOCATION 'hdfs://namenode/user/hive/userdata'
 TBLPROPERTIES ('avro.schema.url'='hdfs://namenode/user/hive/estructura/userdata.avsc');

 show tables;

 describe formatted usuarios;

 CREATE TABLE IF NOT EXISTS summary AS
 SELECT country, COUNT(*) AS user_count
 FROM usuarios
 GROUP BY country
 ORDER BY user_count DESC
 LIMIT 10;

'''