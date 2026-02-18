#!/bin/bash

# Configuration
IMAGE_NAME="ai-vision-rag"
CONTAINER_NAME="ai-vision-rag-app"
PORT=5000

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Change to the project root (parent of scripts/)
cd "$SCRIPT_DIR/.."

echo "🚀 Starting CI/CD Deployment for $IMAGE_NAME..."

# Step 1: Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found in $(pwd)! GEMINI_API_KEY is required for the app to function properly."
    echo "Please create a .env file with GEMINI_API_KEY=your_key_here"
    exit 1
fi

# Step 2: Stop and Remove Existing Container
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🛑 Stopping and removing existing container: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Step 3: Build Docker Image
echo "🛠️ Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

# Step 4: Run Container
echo "🏃 Starting new container: $CONTAINER_NAME on port $PORT"
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    --restart unless-stopped \
    --env-file .env \
    $IMAGE_NAME

echo "✨ Deployment successful! Access the app at http://localhost:$PORT"
echo "📊 Run 'bash scripts/log_monitor.sh' to see application logs."
