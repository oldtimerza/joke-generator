#!/bin/bash

# GitHub Secrets Setup Helper Script
# This script helps you set up the required secrets for GitHub Actions

set -e

echo "🔐 GitHub Secrets Setup Helper"
echo "=============================="
echo ""
echo "This script will help you configure the required secrets for GitHub Actions deployment."
echo "You'll need to add these secrets manually in your GitHub repository:"
echo "Settings → Secrets and variables → Actions → New repository secret"
echo ""

# Function to prompt for input
prompt_secret() {
    local name=$1
    local description=$2
    local example=$3
    
    echo "📝 $name"
    echo "   Description: $description"
    if [ -n "$example" ]; then
        echo "   Example: $example"
    fi
    echo "   Value: [Enter your value, or press Enter to skip]"
    read -r value
    
    if [ -n "$value" ]; then
        echo "   ✅ Value entered for $name"
        echo "   Add this secret in GitHub: $name = [your value]"
    else
        echo "   ⏭️  Skipped $name"
    fi
    echo ""
}

echo "🔧 Required Secrets:"
echo "==================="

prompt_secret "DOCKERHUB_USERNAME" \
    "Your Docker Hub username" \
    "johndoe"

prompt_secret "DOCKERHUB_TOKEN" \
    "Docker Hub access token (create in Account Settings → Security)" \
    "dckr_pat_abc123..."

prompt_secret "DO_HOST" \
    "Digital Ocean droplet IP address" \
    "192.168.1.100"

prompt_secret "DO_USERNAME" \
    "SSH username for your droplet" \
    "root"

echo "🔑 SSH Key Setup:"
echo "================"
echo "For DO_SSH_KEY, you need to generate an SSH key pair:"
echo ""
echo "1. Generate SSH key:"
echo "   ssh-keygen -t ed25519 -C 'github-actions' -f ~/.ssh/github_actions"
echo ""
echo "2. Copy public key to your droplet:"
echo "   ssh-copy-id -i ~/.ssh/github_actions.pub user@your-droplet-ip"
echo ""
echo "3. Copy private key content for GitHub secret:"
echo "   cat ~/.ssh/github_actions"
echo ""
echo "4. Add the private key content as DO_SSH_KEY secret in GitHub"
echo ""

echo "🔧 Optional Secrets:"
echo "==================="

prompt_secret "DO_PORT" \
    "SSH port for your droplet (default: 22)" \
    "22"

prompt_secret "SLACK_WEBHOOK" \
    "Slack webhook URL for deployment notifications" \
    "https://hooks.slack.com/services/..."

echo ""
echo "📋 Configuration Updates Needed:"
echo "================================"
echo ""
echo "1. Update .github/workflows/deploy.yml:"
echo "   Change: DOCKER_IMAGE: your-dockerhub-username/joke-generator"
echo "   To:     DOCKER_IMAGE: [your-dockerhub-username]/joke-generator"
echo ""
echo "2. Update scripts/deploy-to-droplet.sh:"
echo "   Change: GITHUB_REPO=\"your-username/joke-generator\""
echo "   To:     GITHUB_REPO=\"[your-github-username]/[your-repo-name]\""
echo ""
echo "3. Create Docker Hub repository:"
echo "   - Go to hub.docker.com"
echo "   - Create new repository: [your-username]/joke-generator"
echo "   - Set visibility (public/private)"
echo ""

echo "🚀 Testing Deployment:"
echo "====================="
echo ""
echo "1. Test manual deployment first:"
echo "   ssh user@your-droplet-ip"
echo "   export DOCKER_IMAGE=\"your-dockerhub-username/joke-generator:latest\""
echo "   export GITHUB_REPO=\"your-username/joke-generator\""
echo "   curl -fsSL https://raw.githubusercontent.com/\${GITHUB_REPO}/main/scripts/deploy-to-droplet.sh | bash"
echo ""
echo "2. Push to main branch to trigger automatic deployment"
echo ""

echo "✅ Setup complete! Add the secrets to GitHub and update the configuration files."
echo "📖 For detailed instructions, see CICD_SETUP.md"