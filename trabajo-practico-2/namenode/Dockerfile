FROM apache/hadoop:3

# Establecer el directorio de trabajo
WORKDIR /trabajo-practico-2

# Copiar los scripts necesarios
COPY /namenode/init_hdfs.sh init_hdfs.sh
USER root
RUN chmod +x init_hdfs.sh

# Ejecutar el script al iniciar el contenedor
CMD ["/bin/bash", "./init_hdfs.sh"]
