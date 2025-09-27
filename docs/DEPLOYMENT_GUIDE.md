# 🚀 RxFlow Pharmacy Assistant - Deployment Guide

**Version 1.0** | **Last Updated:** September 27, 2025

This comprehensive guide covers all aspects of deploying the RxFlow Pharmacy Assistant to various environments, from development to production scale.

---

## 📋 Table of Contents

1. [Deployment Overview](#-deployment-overview)
2. [Environment Setup](#-environment-setup)
3. [Local Development Deployment](#-local-development-deployment)
4. [Docker Deployment](#-docker-deployment)
5. [Cloud Platform Deployment](#-cloud-platform-deployment)
6. [Kubernetes Deployment](#-kubernetes-deployment)
7. [Production Configuration](#-production-configuration)
8. [Monitoring & Observability](#-monitoring--observability)
9. [Security Considerations](#-security-considerations)
10. [Performance Optimization](#-performance-optimization)
11. [Backup & Recovery](#-backup--recovery)
12. [Troubleshooting](#-troubleshooting)

---

## 🎯 Deployment Overview

### Architecture Components

```
RxFlow Deployment Architecture
┌─────────────────────────────────────────────────────────┐
│                   Load Balancer                         │
├─────────────────────────────────────────────────────────┤
│           Streamlit Application Instances               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   App #1    │  │   App #2    │  │   App #3    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│                 Session Storage                         │
│  ┌─────────────────────────────────────────────────────┐│
│  │                Redis Cluster                        ││
│  └─────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────┤
│                External Services                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ LLM Service │  │ RxNorm API  │  │ GoodRx API  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### Deployment Targets

| Environment | Use Case | Complexity | Scalability |
|-------------|----------|------------|-------------|
| **Local Development** | Testing & Development | Low | Single User |
| **Docker Single Node** | Demo & Small Teams | Medium | 10-50 Users |
| **Docker Compose** | Department Deployment | Medium | 50-200 Users |
| **Cloud Platform** | Enterprise Deployment | High | 200-10k Users |
| **Kubernetes** | Large Scale Enterprise | Very High | 10k+ Users |

---

## ⚙️ Environment Setup

### Prerequisites

#### System Requirements

**Minimum Requirements:**
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB available space
- **OS**: Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+

**Recommended Production:**
- **CPU**: 8 cores
- **RAM**: 16GB
- **Storage**: 50GB SSD
- **OS**: Linux (Ubuntu 22.04 LTS)

#### Software Dependencies

```bash
# Core Requirements
Python 3.12+
Poetry 1.7+
Git 2.30+

# Container Requirements (if using Docker)
Docker 24.0+
Docker Compose 2.20+

# Cloud Requirements (if using cloud platforms)
kubectl 1.28+ (for Kubernetes)
terraform 1.5+ (for infrastructure as code)
```

### Environment Variables

Create environment configuration files for each deployment target:

#### `.env.development`
```bash
# Development Environment
RXFLOW_ENV=development
RXFLOW_DEBUG_MODE=true
RXFLOW_LOG_LEVEL=DEBUG

# LLM Configuration
RXFLOW_LLM_PROVIDER=ollama
RXFLOW_LLM_MODEL=llama3.2
RXFLOW_LLM_BASE_URL=http://localhost:11434

# API Keys (use test/mock keys in development)
RXFLOW_RXNORM_API_KEY=development_key
RXFLOW_GOODRX_API_KEY=development_key

# Session Configuration
RXFLOW_SESSION_TIMEOUT=7200
RXFLOW_REDIS_URL=redis://localhost:6379/0

# Security (use weak settings for development)
RXFLOW_SECRET_KEY=development_secret_key_change_in_production
RXFLOW_ENABLE_RATE_LIMITING=false
```

#### `.env.staging`
```bash
# Staging Environment
RXFLOW_ENV=staging
RXFLOW_DEBUG_MODE=false
RXFLOW_LOG_LEVEL=INFO

# LLM Configuration
RXFLOW_LLM_PROVIDER=openai
RXFLOW_LLM_MODEL=gpt-4
OPENAI_API_KEY=${OPENAI_API_KEY}

# API Keys
RXFLOW_RXNORM_API_KEY=${RXNORM_API_KEY}
RXFLOW_GOODRX_API_KEY=${GOODRX_API_KEY}

# Session Configuration
RXFLOW_SESSION_TIMEOUT=3600
RXFLOW_REDIS_URL=redis://staging-redis:6379/0

# Security
RXFLOW_SECRET_KEY=${SECRET_KEY}
RXFLOW_ENABLE_RATE_LIMITING=true
RXFLOW_RATE_LIMIT_PER_MINUTE=30
```

#### `.env.production`
```bash
# Production Environment
RXFLOW_ENV=production
RXFLOW_DEBUG_MODE=false
RXFLOW_LOG_LEVEL=WARNING

# LLM Configuration
RXFLOW_LLM_PROVIDER=openai
RXFLOW_LLM_MODEL=gpt-4
OPENAI_API_KEY=${OPENAI_API_KEY}

# API Keys
RXFLOW_RXNORM_API_KEY=${RXNORM_API_KEY}
RXFLOW_GOODRX_API_KEY=${GOODRX_API_KEY}

# Session Configuration
RXFLOW_SESSION_TIMEOUT=1800
RXFLOW_REDIS_URL=${REDIS_CLUSTER_URL}

# Security
RXFLOW_SECRET_KEY=${SECRET_KEY}
RXFLOW_ENABLE_RATE_LIMITING=true
RXFLOW_RATE_LIMIT_PER_MINUTE=60

# Monitoring
RXFLOW_ENABLE_METRICS=true
RXFLOW_METRICS_PORT=9090
RXFLOW_HEALTH_CHECK_INTERVAL=30

# Performance
RXFLOW_MAX_WORKERS=4
RXFLOW_WORKER_TIMEOUT=300
```

---

## 💻 Local Development Deployment

### Quick Start Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd rxflow_pharmacy_assistant

# 2. Install dependencies
poetry install

# 3. Set up environment
cp .env.development .env

# 4. Start local LLM (if using Ollama)
ollama serve
ollama pull llama3.2

# 5. Start Redis (if needed)
redis-server

# 6. Start application
poetry run streamlit run app.py

# Application will be available at http://localhost:8501
```

### Development with Auto-reload

```bash
# Install development dependencies
poetry install --with dev

# Start with file watching
poetry run streamlit run app.py --server.fileWatcherType poll

# Or use make command
make dev
```

### Development Testing

```bash
# Run full test suite
make test

# Run specific test categories
make test-unit
make test-integration

# Run with coverage
make test-coverage

# Lint and format code
make lint
make format
```

---

## 🐳 Docker Deployment

### Single Container Deployment

#### Dockerfile
```dockerfile
# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Build and Run
```bash
# Build image
docker build -t rxflow-pharmacy-assistant:latest .

# Run container
docker run -d \
  --name rxflow-app \
  -p 8501:8501 \
  --env-file .env.production \
  rxflow-pharmacy-assistant:latest

# View logs
docker logs -f rxflow-app

# Access application at http://localhost:8501
```

### Multi-Container Deployment with Docker Compose

#### docker-compose.yml
```yaml
version: '3.8'

services:
  # Main Application
  rxflow-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - RXFLOW_ENV=production
      - RXFLOW_REDIS_URL=redis://redis:6379/0
    env_file:
      - .env.production
    depends_on:
      - redis
    volumes:
      - ./data:/app/data:ro
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - rxflow-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis for Session Storage
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - rxflow-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Load Balancer (for scaling)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - rxflow-app
    restart: unless-stopped
    networks:
      - rxflow-network

  # Prometheus for Metrics (optional)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped
    networks:
      - rxflow-network

volumes:
  redis-data:
  prometheus-data:

networks:
  rxflow-network:
    driver: bridge
```

#### Nginx Configuration
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream rxflow_backend {
        server rxflow-app:8501;
        # Add more servers for scaling:
        # server rxflow-app-2:8501;
        # server rxflow-app-3:8501;
    }

    server {
        listen 80;
        server_name localhost;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # Proxy configuration
        location / {
            proxy_pass http://rxflow_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://rxflow_backend/_stcore/health;
        }
    }
}
```

#### Deploy with Docker Compose
```bash
# Start all services
docker-compose up -d

# Scale application instances
docker-compose up -d --scale rxflow-app=3

# View logs
docker-compose logs -f rxflow-app

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## ☁️ Cloud Platform Deployment

### AWS Deployment

#### ECS (Elastic Container Service) Deployment

##### Task Definition
```json
{
  "family": "rxflow-pharmacy-assistant",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/rxflow-task-role",
  "containerDefinitions": [
    {
      "name": "rxflow-app",
      "image": "YOUR_ECR_REPOSITORY:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "RXFLOW_ENV",
          "value": "production"
        },
        {
          "name": "RXFLOW_REDIS_URL",
          "value": "redis://rxflow-redis.cache.amazonaws.com:6379"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:rxflow/openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/rxflow-pharmacy-assistant",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8501/_stcore/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

##### Terraform Configuration
```hcl
# terraform/aws/main.tf

# VPC and Networking
resource "aws_vpc" "rxflow_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "rxflow-vpc"
  }
}

resource "aws_subnet" "rxflow_public_subnet" {
  count             = 2
  vpc_id            = aws_vpc.rxflow_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "rxflow-public-subnet-${count.index + 1}"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "rxflow_cluster" {
  name = "rxflow-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Service
resource "aws_ecs_service" "rxflow_service" {
  name            = "rxflow-service"
  cluster         = aws_ecs_cluster.rxflow_cluster.id
  task_definition = aws_ecs_task_definition.rxflow_task.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.rxflow_public_subnet[*].id
    security_groups = [aws_security_group.rxflow_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.rxflow_tg.arn
    container_name   = "rxflow-app"
    container_port   = 8501
  }

  depends_on = [aws_lb_listener.rxflow_listener]
}

# Application Load Balancer
resource "aws_lb" "rxflow_alb" {
  name               = "rxflow-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.rxflow_alb_sg.id]
  subnets            = aws_subnet.rxflow_public_subnet[*].id

  enable_deletion_protection = false
}

resource "aws_lb_target_group" "rxflow_tg" {
  name        = "rxflow-tg"
  port        = 8501
  protocol    = "HTTP"
  vpc_id      = aws_vpc.rxflow_vpc.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/_stcore/health"
    matcher             = "200"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "rxflow_cache_subnet" {
  name       = "rxflow-cache-subnet"
  subnet_ids = aws_subnet.rxflow_private_subnet[*].id
}

resource "aws_elasticache_replication_group" "rxflow_redis" {
  description          = "Redis for RxFlow sessions"
  replication_group_id = "rxflow-redis"
  
  node_type            = "cache.t3.micro"
  port                 = 6379
  parameter_group_name = "default.redis7"
  
  num_cache_clusters = 2
  
  subnet_group_name  = aws_elasticache_subnet_group.rxflow_cache_subnet.name
  security_group_ids = [aws_security_group.rxflow_redis_sg.id]
}
```

#### Deploy to AWS
```bash
# 1. Build and push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-west-2.amazonaws.com

docker build -t rxflow-pharmacy-assistant .
docker tag rxflow-pharmacy-assistant:latest ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/rxflow-pharmacy-assistant:latest
docker push ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/rxflow-pharmacy-assistant:latest

# 2. Deploy infrastructure with Terraform
cd terraform/aws
terraform init
terraform plan
terraform apply

# 3. Update ECS service
aws ecs update-service \
  --cluster rxflow-cluster \
  --service rxflow-service \
  --force-new-deployment
```

### Google Cloud Platform Deployment

#### Cloud Run Deployment
```bash
# 1. Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/rxflow-pharmacy-assistant

# 2. Deploy to Cloud Run
gcloud run deploy rxflow-pharmacy-assistant \
  --image gcr.io/PROJECT-ID/rxflow-pharmacy-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars RXFLOW_ENV=production \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10
```

### Microsoft Azure Deployment

#### Container Instances Deployment
```bash
# 1. Create resource group
az group create --name rxflow-rg --location eastus

# 2. Create container registry
az acr create --resource-group rxflow-rg --name rxflowregistry --sku Basic

# 3. Build and push image
az acr build --registry rxflowregistry --image rxflow-pharmacy-assistant .

# 4. Deploy container instance
az container create \
  --resource-group rxflow-rg \
  --name rxflow-app \
  --image rxflowregistry.azurecr.io/rxflow-pharmacy-assistant:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8501 \
  --environment-variables RXFLOW_ENV=production \
  --secure-environment-variables OPENAI_API_KEY=$OPENAI_API_KEY
```

---

## ☸️ Kubernetes Deployment

### Kubernetes Manifests

#### Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: rxflow
  labels:
    name: rxflow
```

#### ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rxflow-config
  namespace: rxflow
data:
  RXFLOW_ENV: "production"
  RXFLOW_DEBUG_MODE: "false"
  RXFLOW_LOG_LEVEL: "INFO"
  RXFLOW_REDIS_URL: "redis://redis-service:6379/0"
  RXFLOW_SESSION_TIMEOUT: "1800"
  RXFLOW_ENABLE_RATE_LIMITING: "true"
  RXFLOW_RATE_LIMIT_PER_MINUTE: "60"
```

#### Secret
```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: rxflow-secrets
  namespace: rxflow
type: Opaque
data:
  OPENAI_API_KEY: <base64-encoded-key>
  RXNORM_API_KEY: <base64-encoded-key>
  GOODRX_API_KEY: <base64-encoded-key>
  SECRET_KEY: <base64-encoded-secret>
```

#### Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rxflow-app
  namespace: rxflow
  labels:
    app: rxflow-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rxflow-app
  template:
    metadata:
      labels:
        app: rxflow-app
    spec:
      containers:
      - name: rxflow-app
        image: rxflow-pharmacy-assistant:latest
        ports:
        - containerPort: 8501
        envFrom:
        - configMapRef:
            name: rxflow-config
        - secretRef:
            name: rxflow-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
        imagePullPolicy: Always
      restartPolicy: Always
```

#### Service
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: rxflow-service
  namespace: rxflow
spec:
  selector:
    app: rxflow-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
  type: ClusterIP
```

#### Ingress
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rxflow-ingress
  namespace: rxflow
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
spec:
  tls:
  - hosts:
    - rxflow.yourdomain.com
    secretName: rxflow-tls
  rules:
  - host: rxflow.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: rxflow-service
            port:
              number: 80
```

#### Redis StatefulSet
```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
  namespace: rxflow
spec:
  serviceName: redis-service
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - --appendonly
        - "yes"
        - --maxmemory
        - "512mb"
        - --maxmemory-policy
        - "allkeys-lru"
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-data
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi

---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: rxflow
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  clusterIP: None
```

#### HorizontalPodAutoscaler
```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rxflow-hpa
  namespace: rxflow
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rxflow-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
# 1. Create namespace and apply configs
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# 2. Deploy Redis
kubectl apply -f k8s/redis.yaml

# 3. Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# 4. Set up autoscaling
kubectl apply -f k8s/hpa.yaml

# 5. Verify deployment
kubectl get pods -n rxflow
kubectl get services -n rxflow
kubectl get ingress -n rxflow

# 6. View logs
kubectl logs -f deployment/rxflow-app -n rxflow

# 7. Scale manually if needed
kubectl scale deployment rxflow-app --replicas=5 -n rxflow
```

---

## 🔧 Production Configuration

### Security Configuration

#### SSL/TLS Setup
```bash
# Generate SSL certificates with Let's Encrypt
certbot certonly --standalone -d yourdomain.com

# Or use cert-manager in Kubernetes
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

#### Environment Hardening
```bash
# Production environment variables
export RXFLOW_SECRET_KEY=$(openssl rand -hex 32)
export RXFLOW_ENABLE_RATE_LIMITING=true
export RXFLOW_RATE_LIMIT_PER_MINUTE=60
export RXFLOW_SESSION_TIMEOUT=1800
export RXFLOW_ENABLE_HTTPS_ONLY=true
export RXFLOW_SECURE_COOKIES=true
```

### Performance Configuration

#### Streamlit Production Settings
```toml
# .streamlit/config.toml
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
gatherUsageStats = false

[logger]
level = "warning"
messageFormat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

#### Redis Production Configuration
```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
timeout 300
tcp-keepalive 60
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
```

### Database Configuration

#### Session Storage Optimization
```python
# Enhanced session configuration
REDIS_CONFIG = {
    'host': 'redis-cluster.internal',
    'port': 6379,
    'db': 0,
    'password': os.getenv('REDIS_PASSWORD'),
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'retry_on_timeout': True,
    'health_check_interval': 30,
    'max_connections': 50,
    'connection_pool_kwargs': {
        'max_connections': 50,
        'retry_on_timeout': True
    }
}
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics Configuration

#### prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rxflow_rules.yml"

scrape_configs:
  - job_name: 'rxflow-app'
    static_configs:
      - targets: ['rxflow-service:9090']
    scrape_interval: 30s
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-service:6379']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "RxFlow Pharmacy Assistant",
    "tags": ["rxflow"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(rxflow_response_time_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph", 
        "targets": [
          {
            "expr": "rate(rxflow_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(rxflow_errors_total[5m]) / rate(rxflow_requests_total[5m]) * 100",
            "legendFormat": "Error %"
          }
        ]
      }
    ],
    "refresh": "30s"
  }
}
```

### Health Checks

#### Application Health Check
```python
# health.py
from typing import Dict, Any
import time
import psutil
import redis

async def health_check() -> Dict[str, Any]:
    """Comprehensive health check for RxFlow system."""
    checks = {}
    overall_healthy = True
    
    # Check database connectivity
    try:
        redis_client = redis.Redis.from_url(settings.redis_url)
        redis_client.ping()
        checks['redis'] = {'status': 'healthy', 'response_time': '< 10ms'}
    except Exception as e:
        checks['redis'] = {'status': 'unhealthy', 'error': str(e)}
        overall_healthy = False
    
    # Check LLM connectivity
    try:
        start_time = time.time()
        llm = get_conversational_llm()
        llm.invoke("health check")
        response_time = time.time() - start_time
        checks['llm'] = {
            'status': 'healthy', 
            'response_time': f'{response_time:.2f}s'
        }
    except Exception as e:
        checks['llm'] = {'status': 'unhealthy', 'error': str(e)}
        overall_healthy = False
    
    # Check system resources
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    checks['system'] = {
        'status': 'healthy',
        'memory_usage': f'{memory.percent}%',
        'disk_usage': f'{disk.percent}%',
        'cpu_usage': f'{psutil.cpu_percent()}%'
    }
    
    if memory.percent > 90 or disk.percent > 90:
        checks['system']['status'] = 'warning'
    
    return {
        'status': 'healthy' if overall_healthy else 'unhealthy',
        'timestamp': time.time(),
        'checks': checks
    }
```

### Logging Configuration

#### Structured Logging Setup
```python
# Enhanced logging configuration
import structlog
import logging
import sys

def configure_logging(level: str = "INFO", enable_json: bool = True):
    """Configure structured logging for production."""
    
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        stream=sys.stdout,
    )
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Usage in application
logger = structlog.get_logger(__name__)
logger.info("Application started", version="1.0", environment="production")
```

---

## 🔒 Security Considerations

### Network Security

#### Firewall Rules (iptables)
```bash
# Allow SSH (port 22)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS (ports 80, 443)
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow application port (8501) only from load balancer
iptables -A INPUT -p tcp --dport 8501 -s 10.0.0.0/16 -j ACCEPT

# Allow Redis only from application servers
iptables -A INPUT -p tcp --dport 6379 -s 10.0.1.0/24 -j ACCEPT

# Block all other traffic
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Save rules
iptables-save > /etc/iptables/rules.v4
```

#### Security Groups (AWS)
```bash
# Create security group for application
aws ec2 create-security-group \
    --group-name rxflow-app-sg \
    --description "RxFlow Application Security Group"

# Allow HTTP/HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Allow application port from load balancer
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol tcp \
    --port 8501 \
    --source-group sg-yyyyy
```

### Application Security

#### Rate Limiting
```python
# Enhanced rate limiting configuration
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour", "10 per minute"],
    storage_uri="redis://localhost:6379/1"
)

@limiter.limit("5 per minute")
def conversation_endpoint():
    """Rate-limited conversation endpoint."""
    pass
```

#### Input Validation
```python
# Enhanced input validation
from pydantic import BaseModel, validator
import re

class ConversationInput(BaseModel):
    message: str
    session_id: str
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 2000:
            raise ValueError('Message too long')
        # Remove potentially harmful content
        v = re.sub(r'<[^>]+>', '', v)  # Remove HTML tags
        return v.strip()
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]{8,64}$', v):
            raise ValueError('Invalid session ID format')
        return v
```

---

## ⚡ Performance Optimization

### Application Performance

#### Caching Strategy
```python
# Multi-level caching implementation
from functools import lru_cache
import redis
import pickle

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.redis_url)
        self.local_cache = {}
    
    def get(self, key: str):
        # Try local cache first
        if key in self.local_cache:
            return self.local_cache[key]
        
        # Try Redis cache
        redis_value = self.redis_client.get(key)
        if redis_value:
            value = pickle.loads(redis_value)
            # Store in local cache
            if len(self.local_cache) < 1000:
                self.local_cache[key] = value
            return value
        
        return None
    
    def set(self, key: str, value, ttl: int = 300):
        # Store in both caches
        self.local_cache[key] = value
        self.redis_client.setex(key, ttl, pickle.dumps(value))

# Usage with medication lookups
@lru_cache(maxsize=1000)
def get_medication_info_cached(medication_name: str):
    return expensive_medication_lookup(medication_name)
```

#### Connection Pooling
```python
# Enhanced connection pooling
import asyncio
from typing import Dict, Any

class ConnectionPoolManager:
    def __init__(self):
        self.redis_pool = redis.ConnectionPool(
            host=settings.redis_host,
            port=settings.redis_port,
            db=0,
            max_connections=50,
            retry_on_timeout=True,
            socket_timeout=5
        )
        self.llm_pool = {}
    
    def get_redis_connection(self):
        return redis.Redis(connection_pool=self.redis_pool)
    
    async def get_llm_connection(self):
        # Implement LLM connection pooling
        pass
```

### Infrastructure Performance

#### Load Balancer Configuration
```nginx
# nginx.conf - Optimized for high performance
worker_processes auto;
worker_cpu_affinity auto;
worker_rlimit_nofile 65535;

events {
    use epoll;
    worker_connections 4096;
    multi_accept on;
}

http {
    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 30;
    keepalive_requests 100;
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types
        text/plain
        text/css
        application/json
        application/javascript
        text/xml
        application/xml
        text/javascript;
    
    # Connection pooling
    upstream rxflow_backend {
        least_conn;
        server rxflow-app-1:8501 max_fails=3 fail_timeout=30s;
        server rxflow-app-2:8501 max_fails=3 fail_timeout=30s;
        server rxflow-app-3:8501 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    server {
        listen 80;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        
        location / {
            proxy_pass http://rxflow_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            
            # Timeouts
            proxy_connect_timeout 5s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
```

---

## 💾 Backup & Recovery

### Data Backup Strategy

#### Redis Backup
```bash
#!/bin/bash
# redis-backup.sh

REDIS_HOST="localhost"
REDIS_PORT="6379"
BACKUP_DIR="/var/backups/redis"
DATE=$(date +"%Y%m%d_%H%M%S")

# Create backup directory
mkdir -p $BACKUP_DIR

# Create Redis backup
redis-cli -h $REDIS_HOST -p $REDIS_PORT --rdb $BACKUP_DIR/redis_backup_$DATE.rdb

# Compress backup
gzip $BACKUP_DIR/redis_backup_$DATE.rdb

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

# Upload to S3 (optional)
if [ "$AWS_S3_BUCKET" != "" ]; then
    aws s3 cp $BACKUP_DIR/redis_backup_$DATE.rdb.gz s3://$AWS_S3_BUCKET/redis-backups/
fi
```

#### Configuration Backup
```bash
#!/bin/bash
# config-backup.sh

BACKUP_DIR="/var/backups/config"
DATE=$(date +"%Y%m%d_%H%M%S")
APP_DIR="/app"

mkdir -p $BACKUP_DIR

# Backup configuration files
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz \
    $APP_DIR/.env* \
    $APP_DIR/.streamlit/ \
    $APP_DIR/data/ \
    /etc/nginx/nginx.conf \
    /etc/redis/redis.conf

# Clean old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Disaster Recovery

#### Recovery Procedures
```bash
#!/bin/bash
# disaster-recovery.sh

echo "Starting disaster recovery process..."

# 1. Stop services
docker-compose down

# 2. Restore Redis data
echo "Restoring Redis data..."
gunzip -c /var/backups/redis/redis_backup_latest.rdb.gz > /var/lib/redis/dump.rdb

# 3. Restore configuration
echo "Restoring configuration..."
tar -xzf /var/backups/config/config_backup_latest.tar.gz -C /

# 4. Start services
docker-compose up -d

# 5. Verify services
sleep 30
curl -f http://localhost/_stcore/health || echo "Health check failed"

echo "Disaster recovery completed"
```

#### Automated Recovery Testing
```bash
#!/bin/bash
# test-recovery.sh

# Run recovery test monthly
RESTORE_TEST_DIR="/tmp/restore_test"

mkdir -p $RESTORE_TEST_DIR
cd $RESTORE_TEST_DIR

# Download latest backup
aws s3 cp s3://$BACKUP_BUCKET/redis-backups/ . --recursive

# Test Redis restore
redis-server --dir . --dbfilename redis_backup_latest.rdb --daemonize yes --port 6380

# Test connection
redis-cli -p 6380 ping

# Cleanup
redis-cli -p 6380 shutdown nosave
rm -rf $RESTORE_TEST_DIR
```

---

## 🔍 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
docker logs rxflow-app

# Common issues and solutions:

# 1. Port already in use
sudo netstat -tulpn | grep 8501
sudo kill $(sudo lsof -t -i:8501)

# 2. Environment variables missing
docker exec rxflow-app env | grep RXFLOW

# 3. Redis connection failed
docker exec rxflow-app redis-cli -h redis ping

# 4. LLM connection issues
docker exec rxflow-app python -c "from rxflow.llm import get_conversational_llm; print(get_conversational_llm())"
```

#### Performance Issues
```bash
# Monitor resource usage
docker stats rxflow-app

# Check Redis performance
redis-cli --latency -h redis

# Monitor application metrics
curl http://localhost:8501/_stcore/health

# Check system resources
htop
iostat -x 1
```

#### Memory Issues
```bash
# Check memory usage
docker exec rxflow-app python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'Memory %: {process.memory_percent():.2f}%')
"

# Restart application to clear memory leaks
docker restart rxflow-app
```

### Debugging Tools

#### Application Debug Mode
```python
# Enable debug mode
export RXFLOW_DEBUG_MODE=true
export RXFLOW_LOG_LEVEL=DEBUG

# Run with debug server
streamlit run app.py --server.runOnSave=true --logger.level=debug
```

#### Network Debugging
```bash
# Test connectivity between services
docker exec rxflow-app nslookup redis
docker exec rxflow-app telnet redis 6379

# Monitor network traffic
tcpdump -i eth0 port 8501

# Check DNS resolution
docker exec rxflow-app nslookup api.openai.com
```

### Log Analysis

#### Centralized Logging with ELK Stack
```yaml
# elk-stack.yml
version: '3.8'
services:
  elasticsearch:
    image: elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"

  logstash:
    image: logstash:8.8.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"

  kibana:
    image: kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

#### Log Parsing Configuration
```bash
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "rxflow" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "rxflow-logs-%{+YYYY.MM.dd}"
  }
}
```

---

## 📋 Deployment Checklist

### Pre-Deployment Checklist

- [ ] **Environment Setup**
  - [ ] Environment variables configured
  - [ ] Secrets properly stored and encrypted
  - [ ] SSL certificates generated and installed
  - [ ] Database connections tested

- [ ] **Security Configuration**
  - [ ] Firewall rules configured
  - [ ] Rate limiting enabled
  - [ ] Input validation implemented
  - [ ] Security headers configured

- [ ] **Performance Optimization**
  - [ ] Connection pooling configured
  - [ ] Caching strategy implemented
  - [ ] Load balancer configured
  - [ ] Auto-scaling rules defined

- [ ] **Monitoring Setup**
  - [ ] Health checks implemented
  - [ ] Metrics collection configured
  - [ ] Alerting rules defined
  - [ ] Log aggregation setup

- [ ] **Backup Configuration**
  - [ ] Backup procedures tested
  - [ ] Recovery procedures documented
  - [ ] Backup retention policy defined
  - [ ] Disaster recovery plan created

### Post-Deployment Checklist

- [ ] **Functionality Testing**
  - [ ] Application health check passes
  - [ ] All endpoints responding
  - [ ] Database connectivity verified
  - [ ] External API integrations working

- [ ] **Performance Validation**
  - [ ] Response times within acceptable limits
  - [ ] Memory usage stable
  - [ ] CPU utilization reasonable
  - [ ] Database performance acceptable

- [ ] **Security Validation**
  - [ ] SSL certificate working
  - [ ] Rate limiting functional
  - [ ] Security headers present
  - [ ] Vulnerability scan passed

- [ ] **Monitoring Verification**
  - [ ] Metrics being collected
  - [ ] Alerts configured and tested
  - [ ] Logs being aggregated
  - [ ] Dashboards accessible

---

This deployment guide provides comprehensive coverage of deploying RxFlow Pharmacy Assistant across various environments. Choose the deployment strategy that best fits your requirements and scale accordingly as your needs grow.

For additional support and updates, refer to the [User Guide](USER_GUIDE.md), [Developer Guide](DEVELOPER_GUIDE.md), and [API Reference](API_REFERENCE.md).

**Last Updated:** September 27, 2025 | **Version:** 1.0