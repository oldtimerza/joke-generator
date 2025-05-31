# CI/CD Setup Guide

This guide explains how to set up automated deployment from GitHub to Digital Ocean using GitHub Actions.

## Overview

The CI/CD pipeline consists of:
1. **Build & Push**: Builds Docker image and pushes to Docker Hub
2. **Deploy**: Deploys the image to Digital Ocean droplet
3. **Notify**: Sends deployment status notifications (optional)

## Prerequisites

### 1. Docker Hub Account
- Create account at [hub.docker.com](https://hub.docker.com)
- Create a repository (e.g., `your-username/joke-generator`)
- Generate access token in Account Settings > Security

### 2. Digital Ocean Droplet
- Create a droplet with Ubuntu 20.04+ LTS
- Ensure SSH access is configured
- Note the droplet's IP address

### 3. GitHub Repository
- Fork or create repository with this code
- Enable GitHub Actions in repository settings

## GitHub Secrets Configuration

Add the following secrets in your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | `johndoe` |
| `DOCKERHUB_TOKEN` | Docker Hub access token | `dckr_pat_abc123...` |
| `DO_HOST` | Digital Ocean droplet IP | `192.168.1.100` |
| `DO_USERNAME` | SSH username for droplet | `root` or `ubuntu` |
| `DO_SSH_KEY` | Private SSH key for droplet | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

### Optional Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DO_PORT` | SSH port (default: 22) | `22` |
| `SLACK_WEBHOOK` | Slack webhook for notifications | `https://hooks.slack.com/...` |

## Setup Steps

### 1. Update Configuration

Edit `.github/workflows/deploy.yml`:
```yaml
env:
  DOCKER_IMAGE: your-dockerhub-username/joke-generator  # Update this
```

Edit `scripts/deploy-to-droplet.sh`:
```bash
GITHUB_REPO="${GITHUB_REPO:-your-username/joke-generator}"  # Update this
```

### 2. Generate SSH Key for Digital Ocean

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions

# Copy public key to Digital Ocean droplet
ssh-copy-id -i ~/.ssh/github_actions.pub user@your-droplet-ip

# Copy private key content for GitHub secret
cat ~/.ssh/github_actions
```

### 3. Prepare Digital Ocean Droplet

SSH into your droplet and run:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install curl (if not present)
sudo apt install -y curl

# Create deployment directory
sudo mkdir -p /opt/joke-generator
sudo chown $USER:$USER /opt/joke-generator

# Test Docker installation (will be installed automatically if needed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 4. Test Manual Deployment

Before setting up automation, test manual deployment:
```bash
# On your droplet
export DOCKER_IMAGE="your-dockerhub-username/joke-generator:latest"
export GITHUB_REPO="your-username/joke-generator"
curl -fsSL https://raw.githubusercontent.com/${GITHUB_REPO}/main/scripts/deploy-to-droplet.sh | bash
```

## Workflow Triggers

The GitHub Actions workflow triggers on:
- **Push to main/master**: Full build, push, and deploy
- **Pull requests**: Build and push only (no deploy)
- **Manual trigger**: Via GitHub Actions UI

## Workflow Jobs

### 1. Build and Push Job
- Checks out code
- Sets up Docker Buildx
- Logs into Docker Hub
- Builds multi-platform image (amd64, arm64)
- Pushes to Docker Hub
- Runs security scan

### 2. Deploy Job
- Only runs on main/master branch
- SSHs into Digital Ocean droplet
- Downloads deployment files
- Updates and restarts containers
- Performs health check

### 3. Notify Job
- Sends Slack notification (if configured)
- Reports success/failure status

## Security Features

### Docker Image Security
- Non-root user execution
- Minimal base image
- Security scanning with Docker Scout
- Multi-platform builds

### Deployment Security
- SSH key authentication
- Secrets management via GitHub
- Health checks before completion
- Automatic cleanup of old images

### Network Security
- Nginx reverse proxy with security headers
- Rate limiting
- SSL/TLS ready configuration

## Monitoring and Troubleshooting

### View Deployment Logs
```bash
# On Digital Ocean droplet
cd /opt/joke-generator
sudo docker-compose logs -f
```

### Check Container Status
```bash
sudo docker-compose ps
sudo docker stats
```

### Manual Rollback
```bash
# Stop current deployment
sudo docker-compose down

# Pull previous version
sudo docker pull your-dockerhub-username/joke-generator:previous-tag

# Update .env file with previous tag
echo "DOCKER_IMAGE=your-dockerhub-username/joke-generator:previous-tag" > .env

# Start with previous version
sudo docker-compose up -d
```

### Common Issues

1. **SSH Connection Failed**
   - Verify droplet IP and SSH key
   - Check firewall settings
   - Ensure SSH service is running

2. **Docker Build Failed**
   - Check Dockerfile syntax
   - Verify base image availability
   - Review build logs in GitHub Actions

3. **Deployment Health Check Failed**
   - Check application logs
   - Verify port configuration
   - Ensure all dependencies are available

## Production Considerations

### SSL/TLS Setup
1. Obtain SSL certificate (Let's Encrypt recommended)
2. Update nginx.conf with SSL configuration
3. Update GitHub secrets with domain name

### Domain Configuration
1. Point domain to droplet IP
2. Update nginx.conf with domain name
3. Configure SSL certificate for domain

### Backup Strategy
```bash
# Backup database
docker run --rm -v joke_data:/data -v $(pwd):/backup alpine tar czf /backup/backup-$(date +%Y%m%d).tar.gz -C /data .

# Automated backup script
echo "0 2 * * * cd /opt/joke-generator && docker run --rm -v joke_data:/data -v \$(pwd):/backup alpine tar czf /backup/backup-\$(date +\%Y\%m\%d).tar.gz -C /data ." | sudo crontab -
```

### Scaling Considerations
- Use load balancer for multiple droplets
- Consider managed database service
- Implement container orchestration (Kubernetes)
- Set up monitoring and alerting

## Cost Optimization

### Digital Ocean
- Use appropriate droplet size
- Enable monitoring and alerts
- Consider reserved instances for production

### Docker Hub
- Use efficient base images
- Implement image layer caching
- Clean up old images regularly

## Support

For issues with this setup:
1. Check GitHub Actions logs
2. Review droplet system logs
3. Verify all secrets are correctly configured
4. Test manual deployment first

## Example Commands

### Trigger Manual Deployment
```bash
# Via GitHub CLI
gh workflow run deploy.yml

# Via API
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3" \
  https://api.github.com/repos/your-username/joke-generator/actions/workflows/deploy.yml/dispatches \
  -d '{"ref":"main"}'
```

### Update Deployment
```bash
# On droplet - quick update
export DOCKER_IMAGE="your-dockerhub-username/joke-generator:latest"
export GITHUB_REPO="your-username/joke-generator"
curl -fsSL https://raw.githubusercontent.com/${GITHUB_REPO}/main/scripts/deploy-to-droplet.sh | bash
```