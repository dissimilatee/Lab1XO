#!/bin/bash
# Startup-скрипт VM: ставить Docker і запускає образ PARCS.
# Аргумент PARCS береться з метаданих VM (атрибут parcs-args): "master" або "worker <IP master>".
apt-get update -y && apt-get install -y docker.io
ARGS=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/parcs-args)
docker rm -f parcs 2>/dev/null
docker run -d --name parcs --restart=always --network host -e PARCS_ARGS="$ARGS" hummer12007/parcs-node
