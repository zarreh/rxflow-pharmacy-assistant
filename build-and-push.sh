#!/bin/bash

# Build and Push Script for RxFlow Pharmacy Assistant
# This script builds the Docker image and pushes it to Docker Hub

set -e

# Configuration
DOCKER_USERNAME="zarreh"
IMAGE_NAME="rxflow-pharmacy-assistant"
VERSION=${1:-latest}

echo "🚀 Building RxFlow Pharmacy Assistant Docker Image..."

# Build the Docker image with isolation
echo "📦 Building isolated Docker image: ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
docker build --no-cache -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} .

# Also tag as latest if version is specified
if [ "$VERSION" != "latest" ]; then
    echo "🏷️  Tagging as latest..."
    docker tag ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
fi

echo "✅ Build completed successfully!"

# Login to Docker Hub (if not already logged in)
echo "🔐 Logging into Docker Hub..."
if ! docker info | grep -q "Username: ${DOCKER_USERNAME}"; then
    echo "Please login to Docker Hub:"
    docker login
fi

# Push the image
echo "⬆️  Pushing image to Docker Hub..."
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}

if [ "$VERSION" != "latest" ]; then
    echo "⬆️  Pushing latest tag..."
    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
fi

echo "🎉 Successfully pushed ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} to Docker Hub!"

# Display image size
echo "📊 Image information:"
docker images ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}

echo ""
echo "🚀 To run the container:"
echo "docker run -d -p 8080:8080 --env-file .env ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
echo ""
echo "🐳 Or using docker-compose:"
echo "docker-compose up -d"