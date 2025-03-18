FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY export_to_mysql.py .

CMD ["python", "export_to_mysql.py"]
