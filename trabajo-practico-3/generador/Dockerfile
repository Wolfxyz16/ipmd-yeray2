FROM python:3

WORKDIR /trabajo-practico-3

COPY generador/requeriments.txt .
RUN pip install --no-cache-dir -r requeriments.txt

COPY ./generador/generador.py .
RUN chmod +x ./generador.py


CMD [ "sh", "-c", "sleep 10 && python generador.py" ]
