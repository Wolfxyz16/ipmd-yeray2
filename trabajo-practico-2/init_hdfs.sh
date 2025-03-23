#!/bin/bash

# Crear y asignar permisos en HDFS
hdfs dfs -mkdir -p /user/hive
hdfs dfs -chown hive /user/hive

# Crear directorio en HDFS
hdfs dfs -mkdir -p /user/hive/userdata/

# Subir archivos AVRO a HDFS
hdfs dfs -put /trabajo-practico-2/userdata/* /user/hive/userdata/

echo "✅ Datos AVRO cargados en HDFS correctamente."
