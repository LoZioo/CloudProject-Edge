#!/bin/bash

# Variables.
export IMAGES_DIR="images"

export DOCKERHUB_USER="lozioo"
# export DOCKERHUB_USER=$(docker info | sed '/Username:/!d;s/.* //')

# Exit when any command fails.
set -e
