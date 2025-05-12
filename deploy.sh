#!/bin/bash
# Deployment Script for IELTS AI Prep to Google Cloud Platform

# Exit on error
set -e

# Configuration variables - modify these as needed
PROJECT_ID="ielts-ai-prep-prod"
REGION="us-central1"
SERVICE_NAME="ielts-ai-prep"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}IELTS AI Prep - Deployment to Google Cloud Platform${NC}"
echo "This script will build and deploy your application to GCP Cloud Run."
echo -e "Project: ${GREEN}$PROJECT_ID${NC}"
echo -e "Region: ${GREEN}$REGION${NC}"
echo -e "Service: ${GREEN}$SERVICE_NAME${NC}"
echo 

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed.${NC}"
    echo "Please install the Google Cloud SDK from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: docker is not installed.${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Prompt for confirmation
read -p "Do you want to proceed with deployment? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Set default project
echo -e "\n${YELLOW}Setting default project...${NC}"
gcloud config set project $PROJECT_ID

# Build the Docker image
echo -e "\n${YELLOW}Building Docker image...${NC}"
IMAGE_WITH_TAG="$IMAGE_NAME:$(date +%Y%m%d-%H%M%S)"
echo "Building: $IMAGE_WITH_TAG"

# Build the image
docker build -t $IMAGE_WITH_TAG .

# Push the image to Container Registry
echo -e "\n${YELLOW}Pushing image to Google Container Registry...${NC}"
docker push $IMAGE_WITH_TAG

# Tag as latest
docker tag $IMAGE_WITH_TAG $IMAGE_NAME:latest
docker push $IMAGE_NAME:latest

# Deploy to Cloud Run
echo -e "\n${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-cloudsql-instances=$PROJECT_ID:$REGION:ielts-ai-prep-db \
    --set-env-vars="CLOUD_RUN=true" \
    --update-secrets="DB_USER=db-credentials:username,DB_PASS=db-credentials:password,DB_NAME=db-credentials:database,SESSION_SECRET=session-secret:latest" \
    --memory=4Gi \
    --cpu=2 \
    --min-instances=5 \
    --max-instances=100 \
    --port=5000 \
    --execution-environment=gen2 \
    --cpu-throttling=false

# Get the URL of the deployed service
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

echo -e "\n${GREEN}Deployment Complete!${NC}"
echo -e "Your application is now available at: ${GREEN}$SERVICE_URL${NC}"
echo 
echo "To monitor your application:"
echo -e "- Cloud Run Console: ${YELLOW}https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME${NC}"
echo -e "- Logs: ${YELLOW}https://console.cloud.google.com/logs/query?project=$PROJECT_ID${NC}"
echo 
echo "To make changes:"
echo "1. Update your code"
echo "2. Run this deployment script again"