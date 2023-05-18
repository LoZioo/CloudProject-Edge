#!/bin/bash
IMAGE_NAME="outlier-detector"

# Exit when any command fails.
set -e

docker image rm -f ${IMAGE_NAME}:latest
docker build -t ${IMAGE_NAME}:latest .

echo
docker images
echo
