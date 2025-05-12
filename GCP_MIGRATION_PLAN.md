# Google Cloud Platform Migration Plan for IELTS AI Prep

This document outlines the requirements, process, and implementation plan for migrating IELTS AI Prep to Google Cloud Platform to achieve a scalable infrastructure capable of handling up to 500,000 concurrent users.

## Project Requirements

### Google Cloud Account Setup

1. **Create Google Cloud Account**
   - Go to https://cloud.google.com/
   - Click "Get started for free"
   - Sign in with a Google account
   - Complete the registration process including:
     - Contact information
     - Identity verification
     - Payment method (credit card required, but you receive $300 free credit)

2. **Create a New Project**
   - Project name: `ielts-ai-prep-prod`
   - Organization: Select your organization or leave as "No organization"
   - Location: Select appropriate region (based on your primary user locations)

3. **Enable Required APIs**
   - Cloud Run API
   - Cloud SQL Admin API
   - Redis Memorystore API
   - Cloud Storage API
   - Cloud CDN API
   - Cloud Build API
   - Container Registry API
   - Compute Engine API
   - Cloud Logging API
   - Cloud Monitoring API

4. **Setup Billing Alerts**
   - Navigate to Billing > Budgets & alerts
   - Create budget:
     - Name: "IELTS AI Prep Production Budget"
     - Amount: Your monthly budget (recommend starting with $2,000)
     - Set alert thresholds: 50%, 80%, 90%, 100%
     - Configure email notifications

### Required Infrastructure Components

1. **Cloud SQL (PostgreSQL)**
   - Instance type: db-custom-4-15360 (4 vCPUs, 15GB RAM)
   - Storage: 100GB SSD
   - High availability configuration: Yes
   - Automated backups: Daily, 7-day retention
   - Location: Based on primary user region
   - Read replicas: 1 initially (multi-region if needed)

2. **Cloud Run**
   - CPU allocation: 2 vCPU
   - Memory: 4GB per instance
   - Concurrency: 80 requests per instance
   - Min instances: 5
   - Max instances: 100 (initial setting, can be increased)
   - Request timeout: 60 seconds
   - Ingress: Allow all traffic
   - Container port: 5000

3. **Memorystore (Redis)**
   - Tier: Standard
   - Capacity: 5GB (initial)
   - Version: Redis 6.x
   - Region: Same as Cloud SQL

4. **Cloud Storage**
   - Create 3 buckets:
     - `ielts-ai-prep-media` (public access, for static assets)
     - `ielts-ai-prep-transcripts` (private, for assessment transcripts)
     - `ielts-ai-prep-backups` (private, for database backups)
   - Location type: Multi-region

5. **Cloud CDN**
   - Connect to `ielts-ai-prep-media` bucket
   - Configure cache TTL: 1 day for static assets
   - Enable compression

6. **Load Balancing**
   - Type: Global external HTTP(S) load balancer
   - Frontend configuration:
     - Protocol: HTTPS
     - IP version: IPv4
     - Port: 443
   - Backend configuration:
     - Backend service: Cloud Run service
     - Security: Enable Cloud Armor (for DDoS protection)

## Migration Plan & Implementation Steps

### Phase 1: Application Preparation (1-2 weeks)

1. **Containerize Application**
   - Create Dockerfile
   - Build and test locally
   - Setup environment variable management

2. **Database Migration Plan**
   - Export current database schema
   - Create migration scripts
   - Set up test environment to validate migration

3. **Environment Configuration**
   - Create environment variable sets
   - Setup secrets management
   - Configure Cloud SQL connection

### Phase 2: Initial Deployment (2-3 weeks)

1. **Cloud SQL Setup**
   - Create instance
   - Set up networking and security
   - Run schema migration
   - Import data
   - Configure read replicas

2. **Cloud Run Deployment**
   - Push container image to Container Registry
   - Deploy to Cloud Run
   - Configure environment variables
   - Set up domain mapping

3. **Session Storage Setup**
   - Deploy Redis instance
   - Update application to use Redis for sessions
   - Test session persistence

4. **Static Asset Migration**
   - Upload static files to Cloud Storage
   - Configure CDN
   - Update application to use CDN URLs

### Phase 3: Optimization & Scaling (2-3 weeks)

1. **Load Testing**
   - Create test scripts simulating real user behavior
   - Run incremental load tests
   - Identify and fix bottlenecks

2. **Monitoring Setup**
   - Configure custom metrics
   - Create dashboards for key performance indicators
   - Set up alerts for critical thresholds

3. **Security Hardening**
   - Enable Cloud Armor protection
   - Configure IAM permissions
   - Implement SSL policies

4. **Autoscaling Tuning**
   - Analyze usage patterns
   - Optimize autoscaling parameters
   - Configure scheduled scaling for predictable load patterns

### Phase 4: Global Distribution (Optional, based on user base)

1. **Multi-Regional Deployment**
   - Deploy read replicas to additional regions
   - Set up Cloud Run in multiple regions
   - Configure global load balancing

2. **Regional Cache Optimization**
   - Deploy Redis to multiple regions
   - Implement cache synchronization

## Technological Requirements

### Dockerfile Sample

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PORT 5000

# Run with gunicorn
CMD exec gunicorn --bind :$PORT --workers 4 --threads 8 --timeout 60 main:app
```

### Cloud SQL Connection

```python
# Update database configuration in app.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Cloud SQL PostgreSQL Connection
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
db_host = os.environ.get("DB_HOST")

# If running on Cloud Run, use the Cloud SQL Proxy
if os.environ.get("CLOUD_RUN"):
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")
    db_uri = f"postgresql://{db_user}:{db_pass}@/{db_name}?host={db_socket_dir}/{instance_connection_name}"
else:
    # Local development
    db_uri = f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
}

db.init_app(app)
```

### Redis Session Configuration

```python
# Add to app.py for Redis session handling

from flask_session import Session

# Redis configuration
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url(os.environ.get("REDIS_URL"))
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)
sess = Session(app)
```

## Cost Management Strategies

1. **Start Small, Scale as Needed**
   - Begin with the minimum viable infrastructure
   - Gradually increase capacity based on actual usage
   - Use autoscaling to handle traffic fluctuations

2. **Resource Optimization**
   - Schedule downscaling during predictable low-traffic periods
   - Implement proper caching to reduce compute needs
   - Use Cloud Storage lifecycle policies to manage transcript storage

3. **Monitoring and Budgeting**
   - Set up detailed cost monitoring
   - Create separate budget categories for each major component
   - Review usage weekly to identify optimization opportunities

4. **Long-term Discounts**
   - Once usage patterns stabilize, consider:
     - Committed Use Discounts (1-3 year commitments)
     - Reserved Instances for database
     - Sustained Use Discounts (automatic)

## Required Environment Variables

```
# Database Configuration
DB_USER=ieltsaiprep_user
DB_PASS=[secure password]
DB_NAME=ieltsaiprep_db
DB_HOST=localhost
INSTANCE_CONNECTION_NAME=project:region:instance
CLOUD_RUN=true
DB_SOCKET_DIR=/cloudsql

# Redis Configuration
REDIS_URL=redis://[REDIS_HOST]:[REDIS_PORT]

# Session Security
SESSION_SECRET=[secure random string]

# External Services
STRIPE_SECRET_KEY=[from Stripe dashboard]
STRIPE_PUBLISHABLE_KEY=[from Stripe dashboard]
OPENAI_API_KEY=[from OpenAI dashboard]

# Cloud Storage
GCP_STORAGE_BUCKET=ielts-ai-prep-media
GCP_TRANSCRIPTS_BUCKET=ielts-ai-prep-transcripts

# Application Settings
FLASK_ENV=production
ALLOWED_COUNTRIES=CA,US,IN,NP,KW,QA
```

## Security Considerations

1. **Data Encryption**
   - Enable encryption at rest for all storage
   - Use TLS for all connections
   - Implement proper key management

2. **Identity and Access Management**
   - Create service accounts with minimal permissions
   - Use Secret Manager for sensitive credentials
   - Implement proper IAM roles and permissions

3. **Network Security**
   - Configure Cloud Armor protection
   - Implement proper VPC configuration
   - Use private IP connections where possible

4. **Compliance**
   - Maintain GDPR compliance mechanisms
   - Implement proper data retention policies
   - Ensure geographic restrictions are maintained

## Next Steps

1. Create Google Cloud account and project
2. Enable required APIs
3. Begin containerizing the application
4. Set up initial Cloud SQL instance
5. Configure CI/CD pipeline