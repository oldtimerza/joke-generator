#!/bin/bash

# Digital Ocean Droplet Deployment Script
# This script should be run on the Digital Ocean droplet

set -e

# Configuration
APP_NAME="joke-generator"
APP_DIR="/opt/${APP_NAME}"
DOCKER_IMAGE="${DOCKER_IMAGE:-your-dockerhub-username/joke-generator:latest}"
GITHUB_REPO="${GITHUB_REPO:-your-username/joke-generator}"

echo "🚀 Starting deployment of ${APP_NAME}"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p ${APP_DIR}
cd ${APP_DIR}

# Download deployment files from GitHub
echo "📥 Downloading deployment files..."
download_file() {
    local file=$1
    local url="https://raw.githubusercontent.com/${GITHUB_REPO}/main/${file}"
    
    if command -v curl &> /dev/null; then
        sudo curl -fsSL ${url} -o ${file}
    elif command -v wget &> /dev/null; then
        sudo wget -q ${url} -O ${file}
    else
        echo "❌ Neither curl nor wget is available"
        exit 1
    fi
}

download_file "docker-compose.yml"
download_file "nginx.conf"

# Create environment file
echo "⚙️ Setting up environment..."
sudo tee .env > /dev/null <<EOF
DOCKER_IMAGE=${DOCKER_IMAGE}
FLASK_ENV=production
PYTHONUNBUFFERED=1
EOF

# Update docker-compose.yml to use the built image instead of building
echo "🔧 Configuring docker-compose..."
sudo sed -i "s|build: \.|image: ${DOCKER_IMAGE}|g" docker-compose.yml

# Pull the latest image
echo "📦 Pulling Docker image..."
sudo docker pull ${DOCKER_IMAGE}

# Stop existing containers
echo "🛑 Stopping existing containers..."
sudo docker-compose down || true

# Start new containers
echo "🚀 Starting new containers..."
sudo docker-compose --profile production up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Health check
echo "🏥 Performing health check..."
if curl -f http://localhost/health > /dev/null 2>&1 || curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    echo "📋 Container logs:"
    sudo docker-compose logs --tail=50
    exit 1
fi

# Clean up old images
echo "🧹 Cleaning up old images..."
sudo docker image prune -f

# Show running containers
echo "📊 Running containers:"
sudo docker-compose ps

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Application is available at:"
echo "   - HTTP: http://$(curl -s ifconfig.me)"
echo "   - Local: http://localhost"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: sudo docker-compose logs -f"
echo "   - Restart: sudo docker-compose restart"
echo "   - Stop: sudo docker-compose down"
echo "   - Update: curl -fsSL https://raw.githubusercontent.com/${GITHUB_REPO}/main/scripts/deploy-to-droplet.sh | bash"