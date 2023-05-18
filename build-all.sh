#!/bin/bash

# Include common variables.
source config.sh

for image in $(ls $IMAGES_DIR)
do
	./build-image.sh $image
done
