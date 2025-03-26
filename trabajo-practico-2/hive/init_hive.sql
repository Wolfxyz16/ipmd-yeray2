-- Crear tabla externa con formato AVRO
CREATE EXTERNAL TABLE IF NOT EXISTS usuarios
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.avro.AvroSerDe'
STORED AS AVRO
LOCATION 'hdfs://namenode/user/hive/userdata/'
TBLPROPERTIES ('avro.schema.url'='hdfs://namenode:9000/user/hive/userdata.avsc');

-- Crear tabla resumen de usuarios por país
CREATE TABLE IF NOT EXISTS summary AS
SELECT country, COUNT(*) AS user_count
FROM usuarios
GROUP BY country
ORDER BY user_count DESC
LIMIT 10;