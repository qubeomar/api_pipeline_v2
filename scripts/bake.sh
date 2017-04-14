#!/bin/bash
set -o allexport

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

if [ -e .env ]; then
	source .env
fi
echo $ARTIFACTS_DOCKER_IMAGE_LOCAL

docker build -t $ARTIFACTS_DOCKER_IMAGE_LOCAL:$ARTIFACTS_IMAGE_VERSION . 
