FROM python:3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copiar los scripts al contenedor
COPY init_hdfs.sh .
COPY init_hive.sql .
COPY export_to_mariadb.py .

# Dar permisos de ejecución al script de HDFS
RUN chmod +x init_hdfs.sh

# Ejecutar los scripts en el orden correcto
CMD ["/bin/bash", "-c", "
    ./init_hdfs.sh &&
    beeline -u jdbc:hive2://hive-server:10000/ -f init_hive.sql &&
    python3 export_to_mariadb
"]
