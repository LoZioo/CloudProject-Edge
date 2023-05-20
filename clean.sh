#!/bin/bash

# Include common variables.
source config.sh

docker compose rm -f

for image in $(ls -d images/*/ | sed "s/\///g")
do
	docker image rm $DOCKERHUB_USER/$image
done
