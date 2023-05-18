#!/bin/bash

# Include common variables.
source config.sh

for image in $(ls $IMAGES_DIR)
do
	docker push $DOCKERHUB_USER/$image
done
