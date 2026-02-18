#!/bin/bash

CONTAINER_NAME="ai-vision-rag-app"

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🛑 Stopping and removing container: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    echo "✅ Container stopped and removed."
else
    echo "ℹ️ Container $CONTAINER_NAME is not running."
fi
