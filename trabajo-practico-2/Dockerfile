FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY export_to_mysql.py .

CMD ["python", "export_to_mysql.py"]
