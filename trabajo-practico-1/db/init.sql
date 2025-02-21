CREATE USER IF NOT EXISTS 'wolfxyz'@'localhost' IDENTIFIED BY 'wolfxyz';
CREATE USER IF NOT EXISTS 'prometheus'@'localhost' IDENTIFIED WITH unix_socket;
CREATE DATABASE IF NOT EXISTS ipmd;

GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'prometheus'@'localhost';
GRANT ALL PRIVILEGES ON ipmd TO 'wolfxyz'@'localhost';

FLUSH PRIVILEGES;

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
