FROM apache/hadoop:3.4.1

# Establecer el directorio de trabajo
WORKDIR /trabajo-practico-2

# Copiar e instalar dependencias de Python
COPY requeriments.txt .
RUN pip3 install -r requeriments.txt

# Copiar los scripts necesarios
COPY namenode/init_hdfs.sh .
COPY userdata /app/userdata

# Dar permisos de ejecución al script
RUN chmod +x init_hdfs.sh

# Ejecutar el script al iniciar el contenedor
CMD ["bash", "-c", "./init_hdfs.sh"]
