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

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO messages (message) VALUES
('Hello, world!'),
('This is a test message.'),
('Another message for testing.'),
('Lorem ipsum dolor sit amet.'),
('The quick brown fox jumps over the lazy dog.'),
('A journey of a thousand miles begins with a single step.'),
('To be or not to be, that is the question.'),
('All that glitters is not gold.'),
('In the end, we will remember not the words of our enemies, but the silence of our friends.'),
('The only thing we have to fear is fear itself.');
INSERT INTO messages (message) VALUES
('The greatest glory in living lies not in never falling, but in rising every time we fall.'),
('Life is what happens when you’re busy making other plans.'),
('Get busy living or get busy dying.'),
('You have within you right now, everything you need to deal with whatever the world can throw at you.'),
('Believe you can and you’re halfway there.'),
('The only impossible journey is the one you never begin.'),
('Act as if what you do makes a difference. It does.');

