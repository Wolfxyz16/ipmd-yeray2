#!/usr/bin/env bash
cd "$(dirname "$0")"

docker build -t ejecutor ../ejecutor
docker run --name=ejecutor --network=mynet ejecutor
docker image rm ejecutor
