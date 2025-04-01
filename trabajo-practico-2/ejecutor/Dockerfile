FROM python:3

WORKDIR /trabajo-practico-2

COPY requeriments.txt .
RUN pip install --no-cache-dir -r requeriments.txt

COPY ./export_to_mariadb.py ./export_to_mariadb.py

CMD [ "python", "./export_to_mariadb.py" ]
