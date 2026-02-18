#!/bin/bash

# Configuration
CONTAINER_NAME="ai-vision-rag-app"

echo "📋 Tailing logs for container: $CONTAINER_NAME"
echo "💡 Press Ctrl+C to stop monitoring."
echo "------------------------------------------------"

# Check if container is running
if [ ! "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "⚠️ Warning: Container $CONTAINER_NAME is not currently running."
    echo "You can start it with: bash scripts/deploy.sh"
    echo "------------------------------------------------"
fi

# Tail the logs
docker logs -f $CONTAINER_NAME
