#!/bin/bash
# Docker Build Script for Grid-X Worker

set -e  # Exit on error

echo "🏗️  Grid-X Docker Build Script"
echo "=============================="
echo ""

# Check Docker permissions
if ! docker ps &>/dev/null; then
    echo "❌ Docker permission error. Please run one of:"
    echo "   1. Log out and back in (permanent fix)"
    echo "   2. sudo ./build_docker.sh"
    echo "   3. newgrp docker, then run ./build_docker.sh"
    exit 1
fi

# Check disk space
AVAILABLE=$(df / | tail -1 | awk '{print $4}')
echo "📊 Available disk space: $(df -h / | tail -1 | awk '{print $4}')"
if [ "$AVAILABLE" -lt 2000000 ]; then
    echo "⚠️  Warning: Less than 2GB free. Cleaning Docker..."
    docker system prune -f
fi

# Build the image
echo ""
echo "🐳 Building Docker image (this may take 5-10 minutes)..."
cd "$(dirname "$0")"
docker build -f Dockerfile.base -t secure-executor-base:latest .

echo ""
echo "✅ Build complete!"
docker images | grep secure-executor-base
