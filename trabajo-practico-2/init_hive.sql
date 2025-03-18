-- Crear tabla externa en Hive con los datos en HDFS
CREATE EXTERNAL TABLE IF NOT EXISTS usuarios
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.avro.AvroSerDe'
STORED AS AVRO
LOCATION '/user/hive/warehouse/usuarios'
TBLPROPERTIES ('avro.schema.url'='hdfs:///user/hive/warehouse/usuarios/userdata.avsc');

-- Crear tabla resumen con el número de usuarios por país
CREATE TABLE IF NOT EXISTS summary AS
SELECT country, COUNT(*) AS user_count
FROM usuarios
GROUP BY country
ORDER BY user_count DESC
