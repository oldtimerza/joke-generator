# Docker Deployment Guide

This guide explains how to deploy the Joke Generator application using Docker and Docker Compose.

## Quick Start

### Development Mode
```bash
# Build and run the application
docker-compose up --build

# Access the application at http://localhost:5000
```

### Production Mode (with Nginx)
```bash
# Run with nginx reverse proxy
docker-compose --profile production up --build

# Access the application at http://localhost:80
```

## Files Overview

- `Dockerfile` - Multi-stage build with security best practices
- `docker-compose.yml` - Orchestration for development and production
- `nginx.conf` - Reverse proxy configuration with security headers
- `requirements.txt` - Python dependencies
- `.dockerignore` - Excludes unnecessary files from build context

## Security Features

### Dockerfile Security
- Uses non-root user (`appuser`)
- Minimal base image (python:3.11-slim)
- No cache for pip installations
- Health checks included
- Read-only filesystem with specific writable volumes

### Docker Compose Security
- `no-new-privileges` security option
- Read-only containers with tmpfs for temporary files
- Isolated network
- Resource limits can be added

### Nginx Security (Production)
- Rate limiting (10 requests/second)
- Security headers (XSS, CSRF protection)
- Gzip compression
- SSL/TLS ready configuration

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |

## Volumes

- `joke_data` - Persistent storage for SQLite database
- `/tmp` - Temporary files (tmpfs)
- `/app/data` - Application data directory

## Ports

- `5000` - Flask application (internal)
- `80` - HTTP (nginx, production mode)
- `443` - HTTPS (nginx, production mode, requires SSL setup)

## Commands

### Build Only
```bash
docker-compose build
```

### Run in Background
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f joke-generator
```

### Stop Services
```bash
docker-compose down
```

### Clean Up (Remove Volumes)
```bash
docker-compose down -v
```

## Production Deployment

### 1. SSL Certificate Setup
```bash
# Create SSL directory
mkdir ssl

# Add your SSL certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem
```

### 2. Update nginx.conf
- Uncomment HTTPS server block
- Update `server_name` with your domain
- Configure SSL certificate paths

### 3. Environment Variables
```bash
# Create .env file for production
echo "FLASK_ENV=production" > .env
```

### 4. Deploy
```bash
docker-compose --profile production up -d
```

## Monitoring

### Health Checks
The application includes health checks that verify:
- HTTP endpoint accessibility
- Application responsiveness

### Logs
```bash
# Application logs
docker-compose logs joke-generator

# Nginx logs (production)
docker-compose logs nginx
```

## Scaling

### Horizontal Scaling
```bash
# Scale the application to 3 instances
docker-compose up --scale joke-generator=3
```

Note: For multiple instances, you'll need to configure nginx load balancing.

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   sudo lsof -i :5000
   
   # Kill the process or change the port in docker-compose.yml
   ```

2. **Permission Denied**
   ```bash
   # Ensure Docker daemon is running
   sudo systemctl start docker
   
   # Add user to docker group
   sudo usermod -aG docker $USER
   ```

3. **Database Issues**
   ```bash
   # Reset the database volume
   docker-compose down -v
   docker-compose up --build
   ```

### Debug Mode
```bash
# Run with debug output
docker-compose up --build --verbose
```

## Security Considerations

1. **Never run as root in production**
2. **Use secrets management for sensitive data**
3. **Regularly update base images**
4. **Monitor container logs**
5. **Use HTTPS in production**
6. **Implement proper backup strategies**

## Backup Strategy

```bash
# Backup database volume
docker run --rm -v joke_data:/data -v $(pwd):/backup alpine tar czf /backup/joke_data_backup.tar.gz -C /data .

# Restore database volume
docker run --rm -v joke_data:/data -v $(pwd):/backup alpine tar xzf /backup/joke_data_backup.tar.gz -C /data
```