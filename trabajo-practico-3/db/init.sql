-- Creamos los usuarios
CREATE USER IF NOT EXISTS 'wolfxyz'@'%' IDENTIFIED BY 'wolfxyz';

-- Damos privilegios a los usuarios
GRANT ALL PRIVILEGES ON ipmd TO 'wolfxyz'@'%';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'wolfxyz'@'%';
GRANT SLAVE MONITOR ON *.* TO 'wolfxyz'@'%';
GRANT REPLICATION CLIENT ON *.* TO 'wolfxyz'@'%';

-- Aplicamos los privilegios
FLUSH PRIVILEGES;

-- Creamos la base de datos
CREATE DATABASE IF NOT EXISTS ipmd;

USE ipmd;

-- Creamos la tabla mbti_labels
CREATE TABLE IF NOT EXISTS ipmd.mbti_labels (
    id BIGINT UNSIGNED PRIMARY KEY,
    mbti_personality ENUM('INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 'ENFJ', 'ENFP', 
      'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 'ISTP', 'ISFP', 'ESTP', 'ESFP') NOT NULL,
    pers_id TINYINT UNSIGNED NOT NULL
);

-- Cargamos los datos csv a la tabla mbti_labels
LOAD DATA INFILE './mbti_labels.csv'
INTO TABLE mbti_labels
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
IGNORE 1 LINES;
