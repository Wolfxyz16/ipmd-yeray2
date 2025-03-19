-- Creamos los usuarios
CREATE USER IF NOT EXISTS 'wolfxyz'@'%' IDENTIFIED BY 'wolfxyz';

-- Creamos la base de datos
CREATE DATABASE IF NOT EXISTS ipmd;

-- Damos privilegios a los usuarios
-- prometheus necesita todos los permisos para monitorizar
GRANT ALL PRIVILEGES ON ipmd TO 'wolfxyz'@'%';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'wolfxyz'@'%';
GRANT SLAVE MONITOR ON *.* TO 'wolfxyz'@'%';
GRANT REPLICATION CLIENT ON *.* TO 'wolfxyz'@'%';

-- Aplicamos los privilegios
FLUSH PRIVILEGES;

-- Dentro de la base de datos de ipmd, creamos la tabla messages y añadimos dumb data
USE ipmd;

