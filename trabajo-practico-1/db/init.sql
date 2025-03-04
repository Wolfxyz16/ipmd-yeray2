-- Creamos los usuarios
CREATE USER IF NOT EXISTS 'wolfxyz'@'%' IDENTIFIED BY 'wolfxyz';
CREATE USER IF NOT EXISTS 'prometheus'@'%' IDENTIFIED BY 'prometheus';

-- Creamos la base de datos
CREATE DATABASE IF NOT EXISTS ipmd;

-- Damos privilegios a los usuarios
-- prometheus necesita todos los permisos para monitorizar
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'prometheus'@'%';
GRANT ALL PRIVILEGES ON ipmd TO 'wolfxyz'@'%';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'wolfxyz'@'%';
GRANT SLAVE MONITOR ON *.* TO 'wolfxyz'@'%';
GRANT REPLICATION CLIENT ON *.* TO 'wolfxyz'@'%';

-- Aplicamos los privilegios
FLUSH PRIVILEGES;

-- Dentro de la base de datos de ipmd, creamos la tabla messages y añadimos dumb data
USE ipmd;

CREATE TABLE IF NOT EXISTS messages (
  clid INT NOT NULL,
  mess TEXT NOT NULL,
  sid TEXT NOT NULL,
  PRIMARY KEY(clid)
);

INSERT INTO messages (clid, mess, sid) VALUES
(1, 'Hello world from messages table!', 'abc'),
(2, 'Test', 'def'),
(3, 'Yeray2 is the best team from ipmd', 'abc');
