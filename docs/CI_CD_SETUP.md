# CI/CD Pipeline Documentation

## Overview

Automated CI/CD pipeline using GitHub Actions that:
1. Runs tests on every push
2. Builds Docker images
3. Deploys to production automatically
4. Provides rollback capabilities

## Pipeline Stages

### 1. Test Stage

**Triggers:** Every push and pull request

**Actions:**
- Lint code (Black, isort, Flake8)
- Run unit tests
- Run integration tests
- Security scanning (Trivy)
- Generate coverage reports

**Configuration:** `.github/workflows/test.yml`

### 2. Build Stage

**Triggers:** Push to `main` branch (after tests pass)

**Actions:**
- Build Docker images for all services
- Tag with git SHA and `latest`
- Push to Docker Hub
- Cache layers for faster builds

**Configuration:** `.github/workflows/ci_cd.yml`

### 3. Deploy Stage

**Triggers:** 
- Automatic after successful build (main branch)
- Manual via workflow dispatch

**Actions:**
- SSH to production server
- Pull latest code
- Pull Docker images
- Start containers with zero-downtime
- Run health checks
- Rollback on failure

**Configuration:** `.github/workflows/deploy.yml`

## Setup Instructions

### 1. GitHub Secrets

Add these secrets to your GitHub repository:
```
Settings → Secrets and variables → Actions → New repository secret
```

Required secrets:
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token
- `PRODUCTION_HOST`: Server IP address
- `PRODUCTION_USER`: SSH username (e.g., `ubuntu`)
- `SSH_PRIVATE_KEY`: SSH private key for server access
- `SECRET_KEY`: JWT secret key

### 2. Docker Hub Setup
```bash
# Create Docker Hub token
# Login to hub.docker.com
# Account Settings → Security → New Access Token
# Copy token and add to GitHub secrets
```

### 3. Production Server Setup
```bash
# On production server
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create project directory
sudo mkdir -p /opt/distributed-notification-system
sudo chown $USER:$USER /opt/distributed-notification-system

# Clone repository
cd /opt
git clone <your-repo-url> distributed-notification-system
cd distributed-notification-system

# Setup environment
cp .env.example .env
nano .env  # Edit with production values

# Create backup directory
sudo mkdir -p /backup
sudo chown $USER:$USER /backup
```

### 4. SSH Key Setup
```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions

# Copy public key to server
ssh-copy-id -i ~/.ssh/github_actions.pub user@your-server

# Copy private key content
cat ~/.ssh/github_actions
# Add to GitHub secrets as SSH_PRIVATE_KEY
```

## Workflows

### Automatic Deployment
```bash
# Every push to main triggers:
git add .
git commit -m "feat: add new feature"
git push origin main

# Watch progress:
# https://github.com/YOUR_REPO/actions
```

### Manual Deployment
```bash
# Go to GitHub Actions tab
# Select "Deploy to Production" workflow
# Click "Run workflow"
# Select environment (production/staging)
# Select version (docker tag)
# Click "Run workflow"
```

### Rollback
```bash
# Option 1: Via GitHub Actions
# Go to Actions → Deploy to Production → Re-run previous successful deployment

# Option 2: Via SSH
ssh user@server
cd /opt/distributed-notification-system
sudo ./scripts/rollback.sh
```

## Testing Pipeline Locally
```bash
# Test CI/CD locally
./scripts/test_ci_cd.sh

# Test individual components
pytest tests/ -v
docker build -t test-image services/api_gateway
```

## Monitoring Deployments

### GitHub Actions UI
```
Repository → Actions → Select workflow run
```

### Server Logs
```bash
# SSH to server
ssh user@server

# View deployment logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service
docker logs -f api_gateway

# View Traefik logs
docker logs -f traefik
```

## Deployment Flow Diagram
```
┌─────────────┐
│  Git Push   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Run Tests  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Build Docker │
│   Images    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Push to Hub │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Deploy to    │
│ Production  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Health Check │
└──────┬──────┘
       │
    Success ✅
```

## Troubleshooting

### Build Fails
```bash
# Check test logs in GitHub Actions
# Run tests locally
pytest tests/ -v

# Check Docker build
docker build -t test services/api_gateway
```

### Deployment Fails
```bash
# SSH to server
ssh user@server

# Check logs
docker-compose logs

# Check disk space
df -h

# Check Docker status
docker ps -a
```

### Rollback Doesn't Work
```bash
# Manual rollback
cd /opt/distributed-notification-system
docker-compose down
git checkout <previous-commit-hash>
docker-compose up -d
```

## Best Practices

1. **Always test locally first**
```bash
   ./scripts/test_ci_cd.sh
```

2. **Use feature branches**
```bash
   git checkout -b feature/new-feature
   # Make changes
   git push origin feature/new-feature
   # Create PR → Review → Merge to main
```

3. **Monitor after deployment**
   - Check health endpoints
   - Review logs
   - Monitor metrics

4. **Database backups**
   - Automatic before each deployment
   - Manual: `docker exec postgres pg_dump -U postgres notification_db > backup.sql`

5. **Zero-downtime deployments**
   - Watchtower monitors for new images
   - Rolling updates with health checks

## Security

- Never commit secrets to repository
- Use GitHub secrets for sensitive data
- Rotate SSH keys regularly
- Use least-privilege access
- Enable branch protection on `main`

## Performance

- **Build time:** ~3-5 minutes
- **Test time:** ~1-2 minutes
- **Deployment time:** ~2-3 minutes
- **Total pipeline:** ~6-10 minutes

## Future Improvements

- [ ] Add staging environment
- [ ] Implement canary deployments
- [ ] Add performance testing
- [ ] Automated rollback on errors
- [ ] Slack/Discord notifications
- [ ] Database migration automation