#!/bin/bash

# Crear directorio en HDFS
hdfs dfs -mkdir -p /user/hive/warehouse/usuarios

# Subir archivos AVRO a HDFS
hdfs dfs -put ./userdata/ /user/hive/warehouse/userdata/

echo "✅ Datos AVRO cargados en HDFS correctamente."
