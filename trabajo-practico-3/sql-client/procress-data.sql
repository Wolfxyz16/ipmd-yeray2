-- Tenemos que crear estas tablas en el servicio de sql-client
CREATE TABLE personalities (
  id BIGINT,
  mbti_personality STRING,
  pers_id TINYINT
) WITH (
  'connector' = 'jdbc',
  'url' = 'jdbc:mysql://mariadb:3306/ipmd',
  'table-name' = 'mbti_labels',
  'username' = 'wolfxyz',
  'password' = 'wolfxyz'
);

CREATE TABLE ktuits (
  `user_id` BIGINT,
  `tweet` STRING,
  `proctime` AS proctime()
) WITH (
  'connector' = 'kafka',
  'topic' = 'tuits',
  'format' = 'json',
  'scan.startup.mode' = 'earliest-offset',
  'properties.bootstrap.servers' = 'kafka:9092'
);

CREATE TABLE count_per_personality (
  mbti_label STRING,
  cnt BIGINT,
  mbti_index BIGINT,
  PRIMARY KEY (mbti_index) NOT ENFORCED
) WITH (
  'connector' = 'elasticsearch-7',
  'hosts' = 'http://elasticsearch:9200',
  'index' = 'mbti_index'
);

INSERT INTO count_per_personality 
  SELECT 
    mbti_personality, 
    COUNT(*) AS cnt,
    pers_id FROM ktuits
    LEFT JOIN personalities ON ktuits.user_id=personalities.id
    GROUP BY(mbti_personality, pers_id);
