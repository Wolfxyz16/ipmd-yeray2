FROM apache/hive:3.1.3

# Establecer el directorio de trabajo en la raíz del proyecto
WORKDIR /trabajo-practico-2

# Copiar e instalar dependencias de Python
COPY requeriments.txt .
RUN echo "hola mundo"
#RUN pip install -r requeriments.txt

# Copiar los scripts al contenedor
COPY hive/init_hive.sql .
COPY hive/export_to_mariadb.py .
COPY userdata /app/userdata 


CMD ["bash", "-c", "beeline -u jdbc:hive2://localhost:10000/ -f init_hive.sql"]

