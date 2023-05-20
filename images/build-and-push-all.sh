#!/bin/bash

# Include common variables.
source ../config.sh

for image in $(ls)
do
	./build-and-push-image.sh $image
done
