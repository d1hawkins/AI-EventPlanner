#!/bin/bash
# Run the AI Event Planner SaaS application in Docker

set -e

# Configuration
IMAGE_NAME="ai-event-planner-saas"
CONTAINER_NAME="ai-event-planner-saas"
PORT=8000

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    if [ -f .env.saas.example ]; then
        echo "No .env file found. Creating one from .env.saas.example..."
        cp .env.saas.example .env
        echo ".env file created. Please edit it with your configuration."
    else
        echo "No .env file found. Please create one based on .env.saas.example."
        exit 1
    fi
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME -f Dockerfile.saas .

# Check if the container is already running
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "Container is already running. Stopping it..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Run the container
echo "Starting container..."
docker run --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    --env-file .env \
    -d $IMAGE_NAME

# Wait for the container to start
echo "Waiting for the container to start..."
sleep 5

# Check if the container is running
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "Container is running."
    echo "You can access the application at http://localhost:$PORT/static/saas/index.html"
    
    # Open the browser
    if command -v open &> /dev/null; then
        open "http://localhost:$PORT/static/saas/index.html"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:$PORT/static/saas/index.html"
    elif command -v start &> /dev/null; then
        start "http://localhost:$PORT/static/saas/index.html"
    else
        echo "Please open http://localhost:$PORT/static/saas/index.html in your browser."
    fi
    
    # Show logs
    echo "Showing container logs (press Ctrl+C to exit):"
    docker logs -f $CONTAINER_NAME
else
    echo "Error: Container failed to start."
    docker logs $CONTAINER_NAME
    exit 1
fi
