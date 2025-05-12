#!/bin/bash
# Google Cloud Platform Setup Script for IELTS AI Prep
# This script sets up the necessary GCP resources for deployment

# Exit on error
set -e

# Configuration variables - modify these as needed
PROJECT_ID="ielts-ai-prep-prod"
REGION="us-central1"
DB_INSTANCE_NAME="ielts-ai-prep-db"
DB_NAME="ieltsaiprep"
DB_USER="ieltsaiprep_user"
CLOUD_RUN_SERVICE="ielts-ai-prep"
MEDIA_BUCKET="ielts-ai-prep-media"
TRANSCRIPTS_BUCKET="ielts-ai-prep-transcripts"
BACKUPS_BUCKET="ielts-ai-prep-backups"
REDIS_INSTANCE="ielts-ai-prep-redis"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}IELTS AI Prep - Google Cloud Platform Setup${NC}"
echo "This script will set up your GCP environment for deployment."
echo -e "Project: ${GREEN}$PROJECT_ID${NC}"
echo -e "Region: ${GREEN}$REGION${NC}"
echo 

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed.${NC}"
    echo "Please install the Google Cloud SDK from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Prompt for confirmation
read -p "Do you want to proceed with setup? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

echo -e "\n${YELLOW}Step 1: Setting up GCP project${NC}"
# Check if project exists
if gcloud projects describe $PROJECT_ID &> /dev/null; then
    echo "Project $PROJECT_ID already exists."
else
    echo "Creating project $PROJECT_ID..."
    gcloud projects create $PROJECT_ID
fi

# Set as default project
gcloud config set project $PROJECT_ID
echo "Set $PROJECT_ID as the default project."

echo -e "\n${YELLOW}Step 2: Enabling required APIs${NC}"
# Enable required APIs
APIS=(
    "cloudbuild.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "compute.googleapis.com"
    "run.googleapis.com"
    "sqladmin.googleapis.com"
    "redis.googleapis.com"
    "storage.googleapis.com"
    "artifactregistry.googleapis.com"
    "secretmanager.googleapis.com"
    "monitoring.googleapis.com"
    "logging.googleapis.com"
    "cloudbuild.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "Enabling $api..."
    gcloud services enable $api
done

echo -e "\n${YELLOW}Step 3: Creating Cloud Storage buckets${NC}"
# Create Cloud Storage buckets
gcloud storage buckets create gs://$MEDIA_BUCKET --location=$REGION --uniform-bucket-level-access
echo "Created media bucket: $MEDIA_BUCKET"

gcloud storage buckets create gs://$TRANSCRIPTS_BUCKET --location=$REGION --uniform-bucket-level-access
echo "Created transcripts bucket: $TRANSCRIPTS_BUCKET"

gcloud storage buckets create gs://$BACKUPS_BUCKET --location=$REGION --uniform-bucket-level-access
echo "Created backups bucket: $BACKUPS_BUCKET"

echo -e "\n${YELLOW}Step 4: Creating Cloud SQL instance${NC}"
# Generate a secure random password for the database
DB_PASSWORD=$(openssl rand -base64 16)

# Create Cloud SQL instance
echo "Creating Cloud SQL instance (this may take several minutes)..."
gcloud sql instances create $DB_INSTANCE_NAME \
    --tier=db-g1-small \
    --region=$REGION \
    --database-version=POSTGRES_14 \
    --storage-size=10GB \
    --storage-auto-increase \
    --availability-type=zonal \
    --backup-start-time=23:00 \
    --enable-bin-log \
    --root-password=$DB_PASSWORD

# Create database and user
echo "Creating database $DB_NAME..."
gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME

echo "Creating database user $DB_USER..."
gcloud sql users create $DB_USER \
    --instance=$DB_INSTANCE_NAME \
    --password=$DB_PASSWORD

echo -e "\n${YELLOW}Step 5: Creating Redis instance${NC}"
# Create Redis instance
echo "Creating Redis instance (this may take several minutes)..."
gcloud redis instances create $REDIS_INSTANCE \
    --region=$REGION \
    --zone=$REGION-a \
    --size=1 \
    --redis-version=redis_6_x \
    --tier=basic

echo -e "\n${YELLOW}Step 6: Storing secrets in Secret Manager${NC}"
# Create secrets
echo "Creating database credentials secret..."
echo -n "$DB_PASSWORD" | gcloud secrets create db-credentials \
    --replication-policy="automatic" \
    --data-file=-

# Generate a random session secret
SESSION_SECRET=$(openssl rand -base64 32)
echo "Creating session secret..."
echo -n "$SESSION_SECRET" | gcloud secrets create session-secret \
    --replication-policy="automatic" \
    --data-file=-

echo -e "\n${YELLOW}Step 7: Setting up IAM permissions${NC}"
# Get the Cloud Run service account
SERVICE_ACCOUNT=$(gcloud iam service-accounts list --filter="displayName:Compute Engine default service account" --format="value(email)")

# Grant permissions to the service account
echo "Granting Cloud SQL Client role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/cloudsql.client"

echo "Granting Secret Manager Secret Accessor role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"

echo "Granting Storage Object Admin role for buckets..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectAdmin"

echo -e "\n${GREEN}Setup Complete!${NC}"
echo "Your GCP environment has been configured for IELTS AI Prep deployment."
echo 
echo "Database connection information:"
echo -e "- Instance: ${GREEN}$DB_INSTANCE_NAME${NC}"
echo -e "- Database: ${GREEN}$DB_NAME${NC}"
echo -e "- Username: ${GREEN}$DB_USER${NC}"
echo -e "- Password: ${RED}(Stored in Secret Manager)${NC}"
echo 
echo "Redis instance:"
echo -e "- Instance: ${GREEN}$REDIS_INSTANCE${NC}"
echo 
echo "Next steps:"
echo "1. Update the cloud-run-config.yaml file with your project details"
echo "2. Build and push your Docker container"
echo "3. Deploy to Cloud Run"
echo 
echo "Example commands:"
echo -e "${YELLOW}gcloud builds submit --tag gcr.io/$PROJECT_ID/$CLOUD_RUN_SERVICE${NC}"
echo -e "${YELLOW}gcloud run deploy $CLOUD_RUN_SERVICE --image gcr.io/$PROJECT_ID/$CLOUD_RUN_SERVICE --region $REGION --platform managed${NC}"