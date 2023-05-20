#!/bin/bash

# Include common variables.
source config.sh

docker compose rm -f
cd images

for image in $(ls -d */ | sed "s/\///g")
do
	docker image rm $DOCKERHUB_USER/$image
done
