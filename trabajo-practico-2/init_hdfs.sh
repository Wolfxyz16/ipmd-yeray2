#!/bin/bash

# Crear directorio en HDFS
hdfs dfs -mkdir -p /user/hive/warehouse/usuarios

# Subir archivos AVRO a HDFS
hdfs dfs -put /data/usuarios.avro /user/hive/warehouse/usuarios/

echo "✅ Datos AVRO cargados en HDFS correctamente."
