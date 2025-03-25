#!/bin/bash

# Crear y asignar permisos en HDFS
hadoop fs -mkdir -p hdfs://localhost/user/hive
hadoop fs -chown hive hdfs://localhost/user/hive
hadoop fs -mkdir -p hdfs://localhost/user/hive/warehouse
hadoop fs -chown hive hdfs://localhost/user/hive/warehouse
hadoop fs -mkdir -p hdfs://localhost/home/hive
hadoop fs -chown hive hdfs://localhost/home/hive

# Crear directorio en HDFS
hadoop fs -mkdir -p hdfs://localhost/user/hive/userdata/
hadoop fs -chown hive hdfs://localhost/user/hive/userdata/

# Subir archivos AVRO a HDFS
hadoop fs -put /trabajo-practico-2/userdata/* hdfs://localhost/user/hive/userdata/

echo "✅ Datos AVRO cargados en HDFS correctamente."
