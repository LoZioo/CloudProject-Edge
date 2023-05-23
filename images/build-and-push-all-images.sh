#!/bin/bash

# Include common variables.
source config.sh

for image in $(ls -d */ | sed "s/\///g")
do
	./build-and-push-image.sh $image
done
