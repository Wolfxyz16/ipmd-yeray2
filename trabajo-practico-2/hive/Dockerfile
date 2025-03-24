FROM python:3.9

# Establecer el directorio de trabajo en la raíz del proyecto
WORKDIR /trabajo-practico-2

# Copiar e instalar dependencias de Python
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copiar los scripts al contenedor
COPY init_hive.sql .
COPY export_to_mariadb.py .
COPY userdata /app/userdata 


CMD ["/bin/bash", "-c", "
    beeline -u jdbc:hive2://localhost:10000/ -f init_hive.sql &&
    python3 export_to_mariadb.py 
"]
