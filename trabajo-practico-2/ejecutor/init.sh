#!/usr/bin/env bash
cd "$(dirname "$0")"

docker build -t ejecutor ../ejecutor
docker run --name=ejecutor --network=mynet ejecutor

# habría que comprobar que el comando se llega a ejecutar
docker stop ejecutor
docker rm ejecutor
docker image rm ejecutor
