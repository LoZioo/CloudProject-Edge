#!/bin/bash

# Include common variables.
source config.sh

for image in $(ls $IMAGES_DIR)
do
	docker compose rm -f
	docker image rm $DOCKERHUB_USER/$image
done
