#!/bin/bash

# Include common variables.
source config.sh

# Check image-folder-name parameter.
if [ -n "$1" ]; then
	IMAGE_NAME=$1

else
	echo "Usage: $0 image-folder-name"
	exit 1

fi

cd "$IMAGES_DIR/$IMAGE_NAME"

# Rebuild the image.
docker image rm -f $DOCKERHUB_USER/$IMAGE_NAME:latest
docker build -t $DOCKERHUB_USER/$IMAGE_NAME:latest .
