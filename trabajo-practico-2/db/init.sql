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
