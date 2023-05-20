#!/bin/bash

# Include common variables.
source ../config.sh

# Check image-folder-name parameter.
if [ -n "$1" ]; then
	IMAGE_NAME=$1

else
	echo "Usage: $0 image-folder-name"
	exit 1

fi

cd "$IMAGE_NAME"

# Build and push the image.
docker buildx build --push --platform linux/amd64,linux/arm64 -t $DOCKERHUB_USER/$IMAGE_NAME:latest .
