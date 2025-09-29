# � Docker Deployment Guide

This comprehensive guide covers deploying RxFlow Pharmacy Assistant using Docker in production environments.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Docker Hub account (username: `zarreh`)
- OpenAI API key for production use

## 🏗️ Production Dependencies

The production build includes only essential dependencies:

**Production Dependencies:**
- `streamlit` - Web framework
- `langchain` & `langgraph` - AI orchestration
- `langchain-community` & `langchain-openai` - LangChain integrations
- `requests` - HTTP client
- `python-dotenv` - Environment management
- `pydantic` & `pydantic-settings` - Data validation
- `geopy` - Location services (for pharmacy distance calculations)
- `typing-extensions` - Type hints

**Excluded from Production (Dev only):**
- `langchain-ollama` - Local LLM (dev only)
- `faiss-cpu` - Vector database (not implemented)
- `sentence-transformers` - Embeddings (not implemented)
- `numpy` & `pandas` - Data analysis (not used)
- All development tools (pytest, black, mypy, etc.)

## 🐳 Docker Deployment

### 1. Configure Environment

```bash
# Copy production environment template
cp .env.production.example .env

# Edit with your production settings
nano .env
```

**Required Environment Variables:**
```env
OPENAI_API_KEY=your_production_openai_key
DEFAULT_LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
DEBUG=false
LOG_LEVEL=INFO
```

### 2. Build and Push to Docker Hub

```bash
# Build and push the image
./build-and-push.sh

# Or specify a version
./build-and-push.sh v1.0.0
```

### 3. Deploy with Docker Compose

```bash
# Pull and run the latest image
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### 4. Manual Docker Run

```bash
# Run the container directly
docker run -d \
  --name rxflow-pharmacy-assistant \
  -p 8080:8080 \
  --env-file .env \
  zarreh/rxflow-pharmacy-assistant:latest
```

## 🌐 VPS Deployment

### 1. Server Setup

```bash
# Install Docker on your VPS
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Deploy to VPS

```bash
# Clone the repository on your VPS
git clone https://github.com/zarreh/rxflow-pharmacy-assistant.git
cd rxflow-pharmacy-assistant

# Switch to deployment branch
git checkout deployment

# Configure environment
cp .env.production.example .env
nano .env  # Add your production values

# Deploy
docker-compose up -d
```

### 3. Configure Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/rxflow
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 🔍 Monitoring and Health Checks

### Health Check Endpoint
The application includes built-in health checks:
```bash
curl http://localhost:8080/_stcore/health
```

### Container Logs
```bash
# View logs
docker-compose logs -f rxflow-pharmacy-assistant

# View specific container logs
docker logs rxflow-pharmacy-assistant -f
```

### Resource Monitoring
```bash
# Monitor resource usage
docker stats rxflow-pharmacy-assistant

# Check container info
docker inspect rxflow-pharmacy-assistant
```

## 🔧 Production Optimizations

The Docker image is optimized for production:

- **Multi-stage build** for minimal image size
- **Non-root user** for security
- **Health checks** for container orchestration
- **Resource limits** in docker-compose
- **Proper signal handling** for graceful shutdowns

## 🚨 Troubleshooting

### Common Issues

1. **Port 8080 already in use**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8081:8080"  # Use port 8081 instead
   ```

2. **OpenAI API key not working**
   ```bash
   # Check environment variables
   docker exec rxflow-pharmacy-assistant env | grep OPENAI
   ```

3. **Container won't start**
   ```bash
   # Check logs for errors
   docker logs rxflow-pharmacy-assistant
   ```

4. **Out of memory**
   ```bash
   # Increase memory limit in docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 4G
   ```

## 📊 Image Information

- **Base Image**: python:3.12-slim
- **Final Size**: ~500MB (optimized)
- **Architecture**: Multi-arch (amd64, arm64)
- **Security**: Non-root user, minimal dependencies

## 🔄 Updates and Rollbacks

### Update to New Version
```bash
# Pull latest image
docker-compose pull

# Recreate containers
docker-compose up -d

# Or update to specific version
docker-compose -f docker-compose.yml up -d zarreh/rxflow-pharmacy-assistant:v1.1.0
```

### Rollback
```bash
# Rollback to previous version
docker-compose -f docker-compose.yml up -d zarreh/rxflow-pharmacy-assistant:v1.0.0
```