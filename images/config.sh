#!/bin/bash

# Variables.
export BUILD_PLATFORMS="linux/amd64,linux/arm64"

export DOCKERHUB_USER="lozioo"
# export DOCKERHUB_USER=$(docker info | sed '/Username:/!d;s/.* //')

# Exit when any command fails.
set -e
