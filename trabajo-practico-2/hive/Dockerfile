FROM apache/hive:4.0.0

# Establecer el directorio de trabajo
WORKDIR /trabajo-practico-2
USER root

# Asegurar permisos de root para instalar paquetes
RUN apt-get update && apt-get install -y python3-pip 

# Copiar e instalar dependencias de Python
RUN mkdir -p /home/hive/.beeline && chown hive:hive /home/hive/.beeline
USER hive

# Copiar los scripts y datos
COPY hive/init_hive.sql init_hive.sql
COPY userdata /app/userdata 

# # Añadimos los archivos de configuracion
# ADD hive/hive-site.xml /opt/hive/conf/hive-site.xml

# Ejecutar SQL en Hive y luego exportar a MariaDB
CMD [beeline -u jdbc:hive2://localhost:10000/ -f hive/init_hive.sql]
