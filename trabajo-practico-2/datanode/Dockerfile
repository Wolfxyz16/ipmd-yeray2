FROM apache/hadoop:3

# Establecer el directorio de trabajo
WORKDIR /trabajo-practico-2

# Copiar e instalar dependencias de Python
COPY requeriments.txt .
RUN echo "hola mundo"
#RUN pip install -r requeriments.txt

# Copiar los scripts necesarios
COPY datanode/init_hdfs.sh .
COPY userdata /app/userdata



# Ejecutar el script al iniciar el contenedor
#CMD ["bash", "-c", "datanode/init_hdfs.sh"]
