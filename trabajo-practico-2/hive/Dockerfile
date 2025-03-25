FROM apache/hive:3.1.3

# Establecer el directorio de trabajo
WORKDIR /trabajo-practico-2

# Asegurar permisos de root para instalar paquetes
USER root
RUN apt-get update && apt-get install -y python3-pip
# Copiar e instalar dependencias de Python
COPY requeriments.txt .
RUN pip install -r requeriments.txt
USER hive
# Copiar los scripts y datos
COPY hive/init_hive.sql .
COPY hive/export_to_mariadb.py .
COPY userdata /app/userdata 

# Ejecutar SQL en Hive y luego exportar a MariaDB
#CMD bash -c "beeline -u jdbc:hive2://localhost:10000/ -f init_hive.sql && python export_to_mariadb.py"
