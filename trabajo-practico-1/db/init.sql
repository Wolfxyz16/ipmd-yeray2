CREATE USER 'wolfxyz'@'localhost' IDENTIFIED BY 'wolfxyz';

CREATE DATABASE IF NOT EXISTS ipmd;

USE ipmd;

CREATE TABLE IF NOT EXISTS messages (
  clid INT NOT NULL,
  mess TEXT NOT NULL,
  sid TEXT NOT NULL,
  PRIMARY KEY(clid)
);
