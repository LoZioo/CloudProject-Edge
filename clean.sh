#!/bin/bash
cd images

# Include common variables.
source config.sh

docker compose rm -f

for image in $(ls -d */ | sed "s/\///g")
do
	docker image rm $DOCKERHUB_USER/$image
done
