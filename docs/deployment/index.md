# Deployment Guide

## Overview

This guide covers deploying RxFlow Pharmacy Assistant in different environments, from development setups to production healthcare environments with strict security and compliance requirements.

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Memory**: Minimum 4GB RAM, recommended 8GB+ for production
- **Storage**: Minimum 10GB, recommended 50GB+ for logs and data
- **CPU**: 2+ cores recommended for production workloads
- **Network**: HTTPS capability, firewall configuration for healthcare compliance

### Security Requirements

- **Encryption**: TLS 1.3 for data in transit
- **Authentication**: Multi-factor authentication capability
- **Logging**: Comprehensive audit logging for HIPAA compliance
- **Data Protection**: Encryption at rest for patient data
- **Access Control**: Role-based access control (RBAC)

## Development Environment

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/rxflow_pharmacy_assistant.git
cd rxflow_pharmacy_assistant

# Install dependencies using Poetry
poetry install

# Set up environment variables
cp .env.example .env.development
# Edit .env.development with your settings

# Initialize database (if using)
poetry run python -m rxflow.scripts.init_db

# Run development server
poetry run python -m rxflow.main --environment development
```

### Development Docker Setup

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.dev.yml up --build

# Access services:
# - RxFlow App: http://localhost:8000
# - Streamlit UI: http://localhost:8501
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Environment Variables for Development

```bash
# .env.development
ENVIRONMENT=development
DEBUG=true

# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.1

# Database (optional for development)
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=rxflow
DB_PASSWORD=rxflow_dev_pass
DB_DATABASE=rxflow_dev

# Security (development only)
SECRET_KEY=dev-secret-key-change-in-production
ENCRYPTION_KEY=dev-encryption-key-32-chars-long

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/rxflow_dev.log
```

## Staging Environment

### Staging Configuration

Staging should mirror production as closely as possible while allowing for testing:

```bash
# .env.staging
ENVIRONMENT=staging
DEBUG=false

# LLM Configuration (use staging API keys)
LLM_PROVIDER=openai
LLM_API_KEY=your_staging_openai_api_key
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1000

# Database Configuration
DB_HOST=staging-db.internal
DB_PORT=5432
DB_USERNAME=rxflow_staging
DB_PASSWORD=secure_staging_password
DB_DATABASE=rxflow_staging
DB_SSL_MODE=require

# Security
SECRET_KEY=staging-secret-key-64-characters-minimum-for-security
ENCRYPTION_KEY=staging-encryption-key-must-be-32-chars

# External Services
REDIS_URL=redis://staging-redis.internal:6379
PHARMACY_API_URL=https://staging-api.pharmacy.com
PATIENT_API_URL=https://staging-patient-api.internal

# Monitoring
METRICS_ENABLED=true
HEALTH_CHECK_ENABLED=true
LOG_LEVEL=INFO
```

### Staging Docker Setup

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  rxflow-app:
    build:
      context: .
      dockerfile: Dockerfile.staging
    environment:
      - ENVIRONMENT=staging
    env_file:
      - .env.staging
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    networks:
      - rxflow-staging
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: rxflow_staging
      POSTGRES_USER: rxflow_staging
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_staging_data:/var/lib/postgresql/data
    networks:
      - rxflow-staging

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_staging_data:/data
    networks:
      - rxflow-staging

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/staging.conf:/etc/nginx/nginx.conf
      - ./ssl/staging:/etc/nginx/ssl
    depends_on:
      - rxflow-app
    networks:
      - rxflow-staging

volumes:
  postgres_staging_data:
  redis_staging_data:

networks:
  rxflow-staging:
    driver: bridge
```

## Production Deployment

### Production Infrastructure Requirements

For healthcare applications, production deployment requires:

1. **High Availability**: Multiple instances, load balancing, failover
2. **Security**: WAF, DDoS protection, intrusion detection
3. **Compliance**: HIPAA, SOC 2, logging and audit trails
4. **Monitoring**: 24/7 monitoring, alerting, health checks
5. **Backup**: Automated backups, disaster recovery plan

### AWS Production Deployment

#### Infrastructure as Code (Terraform)

```hcl
# terraform/main.tf
provider "aws" {
  region = var.aws_region
}

# VPC Configuration
resource "aws_vpc" "rxflow_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "rxflow-vpc"
    Environment = "production"
  }
}

# Private Subnets for Application
resource "aws_subnet" "private_subnets" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.rxflow_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "rxflow-private-subnet-${count.index + 1}"
  }
}

# RDS Database
resource "aws_db_instance" "rxflow_db" {
  identifier     = "rxflow-production"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.large"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp3"
  storage_encrypted     = true
  
  db_name  = "rxflow_prod"
  username = "rxflow"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.rxflow_db_subnet.name
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "rxflow-final-snapshot"
  
  tags = {
    Name        = "rxflow-production-db"
    Environment = "production"
  }
}

# ECS Cluster for Application
resource "aws_ecs_cluster" "rxflow_cluster" {
  name = "rxflow-production"
  
  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"
      log_configuration {
        cloud_watch_log_group_name = aws_cloudwatch_log_group.ecs_logs.name
      }
    }
  }
  
  tags = {
    Name        = "rxflow-cluster"
    Environment = "production"
  }
}

# Application Load Balancer
resource "aws_lb" "rxflow_alb" {
  name               = "rxflow-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets           = aws_subnet.public_subnets[*].id

  enable_deletion_protection = true
  enable_http2              = true
  
  tags = {
    Name        = "rxflow-alb"
    Environment = "production"
  }
}
```

#### ECS Task Definition

```json
{
  "family": "rxflow-production",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "rxflow-app",
      "image": "your-account.dkr.ecr.us-west-2.amazonaws.com/rxflow:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "LLM_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:account:secret:rxflow/llm-api-key"
        },
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:account:secret:rxflow/db-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/rxflow-production",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### Production Environment Variables

```bash
# .env.production (stored in AWS Secrets Manager)
ENVIRONMENT=production
DEBUG=false

# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=prod_openai_api_key_from_secrets_manager
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1000
LLM_RATE_LIMIT_PER_MINUTE=100

# Database Configuration
DB_HOST=rxflow-production.cluster-xyz.us-west-2.rds.amazonaws.com
DB_PORT=5432
DB_USERNAME=rxflow
DB_PASSWORD=secure_production_password_from_secrets_manager
DB_DATABASE=rxflow_prod
DB_SSL_MODE=require
DB_CONNECTION_POOL_SIZE=20

# Security
SECRET_KEY=production_secret_key_64_characters_minimum_stored_securely
ENCRYPTION_KEY=production_encryption_key_32_chars_secure
JWT_EXPIRY_HOURS=24
RATE_LIMIT_PER_MINUTE=60

# External Services
REDIS_URL=redis://rxflow-prod-cache.abc123.cache.amazonaws.com:6379
PHARMACY_API_URL=https://api.pharmacy.com
PATIENT_API_URL=https://patient-api.healthcare-org.com
RXNORM_API_URL=https://rxnav.nlm.nih.gov/REST

# Monitoring and Logging
METRICS_ENABLED=true
HEALTH_CHECK_ENABLED=true
LOG_LEVEL=INFO
LOG_FORMAT=json
SENTRY_DSN=https://your-sentry-dsn-here

# Feature Flags
ENHANCED_DRUG_CHECKING=true
MULTI_PHARMACY_COMPARISON=true
REAL_TIME_INVENTORY=true
AI_CLINICAL_RECOMMENDATIONS=true

# Compliance
AUDIT_LOGGING=true
HIPAA_COMPLIANT_LOGGING=true
DATA_RETENTION_DAYS=2555  # 7 years for healthcare
```

### Kubernetes Production Deployment

#### Namespace and Configuration

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: rxflow-production
  labels:
    name: rxflow-production
    environment: production

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rxflow-config
  namespace: rxflow-production
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LLM_PROVIDER: "openai"
  LLM_MODEL: "gpt-4"
  LLM_TEMPERATURE: "0.1"
  DB_HOST: "postgres-service.rxflow-production.svc.cluster.local"
  DB_PORT: "5432"
  DB_USERNAME: "rxflow"
  DB_DATABASE: "rxflow_prod"
  LOG_LEVEL: "INFO"
  METRICS_ENABLED: "true"

---
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: rxflow-secrets
  namespace: rxflow-production
type: Opaque
data:
  LLM_API_KEY: <base64-encoded-api-key>
  DB_PASSWORD: <base64-encoded-db-password>
  SECRET_KEY: <base64-encoded-secret-key>
  ENCRYPTION_KEY: <base64-encoded-encryption-key>
```

#### Production Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rxflow-app
  namespace: rxflow-production
  labels:
    app: rxflow-app
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: rxflow-app
  template:
    metadata:
      labels:
        app: rxflow-app
        version: v1.0.0
    spec:
      serviceAccountName: rxflow-service-account
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
      - name: rxflow-app
        image: your-registry.com/rxflow:v1.0.0
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
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
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: tmp
        emptyDir: {}
      - name: logs
        persistentVolumeClaim:
          claimName: rxflow-logs-pvc

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: rxflow-service
  namespace: rxflow-production
  labels:
    app: rxflow-app
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: http
    protocol: TCP
    name: http
  selector:
    app: rxflow-app

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rxflow-ingress
  namespace: rxflow-production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
    nginx.ingress.kubernetes.io/rate-limit-rps: "10"
spec:
  tls:
  - hosts:
    - rxflow.yourdomain.com
    secretName: rxflow-tls-secret
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

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rxflow-hpa
  namespace: rxflow-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rxflow-app
  minReplicas: 3
  maxReplicas: 10
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
```

## Database Management

### Production Database Setup

```sql
-- init_production.sql
-- Create production database with proper permissions and security

-- Create read-only user for reporting
CREATE USER rxflow_readonly WITH PASSWORD 'secure_readonly_password';
GRANT CONNECT ON DATABASE rxflow_prod TO rxflow_readonly;
GRANT USAGE ON SCHEMA public TO rxflow_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rxflow_readonly;

-- Create backup user
CREATE USER rxflow_backup WITH PASSWORD 'secure_backup_password';
GRANT CONNECT ON DATABASE rxflow_prod TO rxflow_backup;
GRANT USAGE ON SCHEMA public TO rxflow_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rxflow_backup;

-- Enable logging for audit trail
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_connections = 'on';
ALTER SYSTEM SET log_disconnections = 'on';
ALTER SYSTEM SET log_checkpoints = 'on';

-- Configure for performance
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;

SELECT pg_reload_conf();
```

### Database Migrations

```python
# scripts/migrate_production.py
import os
import psycopg2
from pathlib import Path

def run_production_migration():
    """Run database migrations in production environment"""
    
    # Production database connection
    conn_params = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', 5432),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': 'require'  # Always use SSL in production
    }
    
    migration_files = sorted(Path('migrations').glob('*.sql'))
    
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            # Create migration tracking table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS migration_history (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum VARCHAR(64) NOT NULL
                )
            """)
            
            # Get applied migrations
            cur.execute("SELECT filename FROM migration_history")
            applied = {row[0] for row in cur.fetchall()}
            
            # Apply new migrations
            for migration_file in migration_files:
                if migration_file.name not in applied:
                    print(f"Applying migration: {migration_file.name}")
                    
                    # Read and execute migration
                    with open(migration_file, 'r') as f:
                        migration_sql = f.read()
                    
                    # Calculate checksum
                    import hashlib
                    checksum = hashlib.sha256(migration_sql.encode()).hexdigest()
                    
                    # Execute migration
                    cur.execute(migration_sql)
                    
                    # Record migration
                    cur.execute(
                        "INSERT INTO migration_history (filename, checksum) VALUES (%s, %s)",
                        (migration_file.name, checksum)
                    )
                    
                    print(f"✅ Migration {migration_file.name} applied successfully")
            
            conn.commit()
            print("🎉 All migrations completed successfully")

if __name__ == "__main__":
    run_production_migration()
```

## Monitoring and Alerting

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rxflow_alerts.yml"

scrape_configs:
  - job_name: 'rxflow-app'
    kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names:
            - rxflow-production
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        action: keep
        regex: rxflow-service
      - source_labels: [__meta_kubernetes_endpoint_port_name]
        action: keep
        regex: metrics

alerting:
  alertmanagers:
    - kubernetes_sd_configs:
        - role: endpoints
          namespaces:
            names:
              - monitoring
      relabel_configs:
        - source_labels: [__meta_kubernetes_service_name]
          regex: alertmanager
          action: keep
```

### Alert Rules

```yaml
# monitoring/rxflow_alerts.yml
groups:
- name: rxflow.rules
  rules:
  - alert: RxFlowHighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate in RxFlow application"
      description: "Error rate is {{ $value }} requests per second"

  - alert: RxFlowHighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time in RxFlow application"
      description: "95th percentile response time is {{ $value }} seconds"

  - alert: RxFlowDatabaseConnectionFailure
    expr: up{job="rxflow-database"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "RxFlow database connection failure"
      description: "Cannot connect to RxFlow database"

  - alert: RxFlowLowDiskSpace
    expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100 < 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Low disk space on RxFlow server"
      description: "Disk space is below 10%"
```

## Backup and Disaster Recovery

### Automated Database Backups

```bash
#!/bin/bash
# scripts/backup_production.sh

set -e

# Configuration
BACKUP_DIR="/backups/rxflow"
RETENTION_DAYS=30
S3_BUCKET="rxflow-production-backups"

# Database configuration from environment
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_DATABASE}
DB_USER=${DB_USERNAME}

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Generate backup filename with timestamp
BACKUP_FILE="${BACKUP_DIR}/rxflow_$(date +%Y%m%d_%H%M%S).sql"

# Create database backup
pg_dump \
  --host=${DB_HOST} \
  --port=${DB_PORT} \
  --username=${DB_USER} \
  --dbname=${DB_NAME} \
  --no-password \
  --format=custom \
  --compress=9 \
  --file=${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_FILE}
BACKUP_FILE="${BACKUP_FILE}.gz"

echo "✅ Database backup created: ${BACKUP_FILE}"

# Upload to S3
aws s3 cp ${BACKUP_FILE} s3://${S3_BUCKET}/database/
echo "✅ Backup uploaded to S3"

# Clean up old backups locally
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
echo "✅ Old local backups cleaned up"

# Clean up old S3 backups (keep last 90 days)
aws s3 ls s3://${S3_BUCKET}/database/ --recursive | \
  awk '{if($1 < "'$(date -d '90 days ago' '+%Y-%m-%d')'") print $4}' | \
  xargs -I {} aws s3 rm s3://${S3_BUCKET}/{}

echo "✅ Old S3 backups cleaned up"
echo "🎉 Backup process completed successfully"
```

### Disaster Recovery Procedures

```bash
#!/bin/bash
# scripts/restore_production.sh

set -e

# Restore from backup file
restore_from_backup() {
    local backup_file=$1
    
    echo "🔄 Starting database restore from ${backup_file}"
    
    # Stop application temporarily
    kubectl scale deployment rxflow-app --replicas=0 -n rxflow-production
    
    # Create new database for restore
    createdb -h ${DB_HOST} -U ${DB_USER} rxflow_restored
    
    # Restore data
    pg_restore \
      --host=${DB_HOST} \
      --port=${DB_PORT} \
      --username=${DB_USER} \
      --dbname=rxflow_restored \
      --clean \
      --if-exists \
      ${backup_file}
    
    echo "✅ Database restored successfully"
    
    # Update application configuration to use restored database
    kubectl patch configmap rxflow-config \
      -p '{"data":{"DB_DATABASE":"rxflow_restored"}}' \
      -n rxflow-production
    
    # Restart application
    kubectl scale deployment rxflow-app --replicas=3 -n rxflow-production
    
    echo "🎉 Disaster recovery completed successfully"
}

# Point-in-time recovery
restore_point_in_time() {
    local target_time=$1
    
    echo "🔄 Starting point-in-time recovery to ${target_time}"
    
    # This would use AWS RDS point-in-time recovery or PostgreSQL WAL-E
    # Implementation depends on your backup strategy
    
    aws rds restore-db-instance-to-point-in-time \
      --source-db-instance-identifier rxflow-production \
      --target-db-instance-identifier rxflow-pitr-restore \
      --restore-time ${target_time}
    
    echo "✅ Point-in-time recovery initiated"
}

# Usage
case "$1" in
    "backup")
        backup_file="$2"
        restore_from_backup "$backup_file"
        ;;
    "pitr")
        target_time="$2"
        restore_point_in_time "$target_time"
        ;;
    *)
        echo "Usage: $0 {backup|pitr} <backup_file_or_target_time>"
        exit 1
        ;;
esac
```

## Security Hardening

### Production Security Checklist

- [ ] **SSL/TLS Configuration**
  - [ ] TLS 1.3 enabled
  - [ ] Strong cipher suites only
  - [ ] HSTS headers configured
  - [ ] Certificate auto-renewal setup

- [ ] **Authentication & Authorization**
  - [ ] Multi-factor authentication enabled
  - [ ] Role-based access control implemented
  - [ ] API key rotation policy in place
  - [ ] Session management configured

- [ ] **Data Protection**
  - [ ] Database encryption at rest
  - [ ] Application-level encryption for PII
  - [ ] Secure key management (AWS KMS/HashiCorp Vault)
  - [ ] Data masking for non-production environments

- [ ] **Network Security**
  - [ ] VPC/Network segmentation
  - [ ] Web Application Firewall (WAF) configured
  - [ ] DDoS protection enabled
  - [ ] Intrusion detection system

- [ ] **Compliance & Auditing**
  - [ ] HIPAA compliance validated
  - [ ] Audit logging enabled
  - [ ] Log retention policy configured
  - [ ] Regular security assessments scheduled

### Security Configuration

```python
# config/security_production.py
import os
from cryptography.fernet import Fernet

class ProductionSecurityConfig:
    """Production security configuration"""
    
    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    FERNET_CIPHER = Fernet(ENCRYPTION_KEY.encode()) if ENCRYPTION_KEY else None
    
    # Authentication
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRY_HOURS = 24
    
    # Password Requirements
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_SPECIAL_CHARS = True
    REQUIRE_MIXED_CASE = True
    REQUIRE_NUMBERS = True
    
    # Rate Limiting
    API_RATE_LIMIT = '100/hour'
    AUTH_RATE_LIMIT = '5/minute'
    
    # Session Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # CORS Configuration
    ALLOWED_ORIGINS = [
        'https://rxflow.yourdomain.com',
        'https://admin.yourdomain.com'
    ]
    
    # Security Headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'"
    }
```

This comprehensive deployment guide provides everything needed to deploy RxFlow Pharmacy Assistant securely in production healthcare environments while maintaining compliance with healthcare regulations and security best practices.