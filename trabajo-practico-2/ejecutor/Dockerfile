FROM alpine:latest

WORKDIR /trabajo-practico-2

COPY requeriments.txt .
RUN apk add --no-cache python3
RUN pip install --no--cache-dir -r requeriments.txt

COPY /ejecutor .

