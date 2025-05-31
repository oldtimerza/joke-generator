#!/bin/bash

# Joke Generator Deployment Script
# This script helps deploy the application using Docker

set -e

echo "🦄 Joke Generator Deployment Script"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Function to display usage
usage() {
    echo "Usage: $0 [OPTION]"
    echo "Options:"
    echo "  dev         Start in development mode"
    echo "  prod        Start in production mode (with nginx)"
    echo "  build       Build the Docker image only"
    echo "  stop        Stop all services"
    echo "  clean       Stop and remove all containers and volumes"
    echo "  logs        Show application logs"
    echo "  help        Show this help message"
}

# Parse command line arguments
case "${1:-dev}" in
    "dev")
        echo "🚀 Starting in development mode..."
        docker-compose up --build
        ;;
    "prod")
        echo "🚀 Starting in production mode with nginx..."
        docker-compose --profile production up --build -d
        echo "✅ Application started!"
        echo "📱 Access at: http://localhost"
        echo "📊 View logs: ./deploy.sh logs"
        ;;
    "build")
        echo "🔨 Building Docker image..."
        docker-compose build
        echo "✅ Build complete!"
        ;;
    "stop")
        echo "🛑 Stopping services..."
        docker-compose down
        echo "✅ Services stopped!"
        ;;
    "clean")
        echo "🧹 Cleaning up containers and volumes..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        echo "✅ Cleanup complete!"
        ;;
    "logs")
        echo "📋 Showing application logs..."
        docker-compose logs -f joke-generator
        ;;
    "help"|"-h"|"--help")
        usage
        ;;
    *)
        echo "❌ Unknown option: $1"
        usage
        exit 1
        ;;
esac