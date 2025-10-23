#!/bin/bash

# Azure Container App Deployment Script
# Deploys the Appliance Research System to Azure Container Apps

set -e

# Configuration
RESOURCE_GROUP="rg-containerappssriparag"
CONTAINER_APP_NAME="ssripaElevateapp"
LOCATION="eastus"
CONTAINER_REGISTRY_NAME="acrelevateapp"
IMAGE_NAME="elevate-app"
IMAGE_TAG="latest"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Azure Container App Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed${NC}"
    echo "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

echo -e "${GREEN}✓ Azure CLI found${NC}"

# Check if logged in
echo "Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo -e "${RED}Not logged in to Azure. Please login:${NC}"
    az login
fi

echo -e "${GREEN}✓ Logged in to Azure${NC}"

# Get subscription info
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo -e "${BLUE}Subscription: ${SUBSCRIPTION_NAME} (${SUBSCRIPTION_ID})${NC}"

# Check if resource group exists
echo ""
echo "Checking resource group..."
if az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}✓ Resource group '${RESOURCE_GROUP}' exists${NC}"
else
    echo -e "${RED}Error: Resource group '${RESOURCE_GROUP}' not found${NC}"
    echo "Please create it first or use an existing resource group"
    exit 1
fi

# Get resource group location
RG_LOCATION=$(az group show --name $RESOURCE_GROUP --query location -o tsv)
echo -e "${BLUE}Resource group location: ${RG_LOCATION}${NC}"

# Create Azure Container Registry (if not exists)
echo ""
echo "Setting up Azure Container Registry..."
if az acr show --name $CONTAINER_REGISTRY_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}✓ Container Registry '${CONTAINER_REGISTRY_NAME}' exists${NC}"
else
    echo "Creating Container Registry..."
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_REGISTRY_NAME \
        --sku Basic \
        --location $RG_LOCATION \
        --admin-enabled true
    echo -e "${GREEN}✓ Container Registry created${NC}"
fi

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $CONTAINER_REGISTRY_NAME --query loginServer -o tsv)
echo -e "${BLUE}ACR Login Server: ${ACR_LOGIN_SERVER}${NC}"

# Build and push Docker image
echo ""
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

echo "Tagging image for ACR..."
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}

echo "Logging in to ACR..."
az acr login --name $CONTAINER_REGISTRY_NAME

echo "Pushing image to ACR..."
docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}

echo -e "${GREEN}✓ Image pushed to ACR${NC}"

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $CONTAINER_REGISTRY_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $CONTAINER_REGISTRY_NAME --query passwords[0].value -o tsv)

# Create Container Apps Environment (if not exists)
echo ""
echo "Setting up Container Apps Environment..."
ENVIRONMENT_NAME="${CONTAINER_APP_NAME}-env"

if az containerapp env show --name $ENVIRONMENT_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}✓ Container Apps Environment exists${NC}"
else
    echo "Creating Container Apps Environment..."
    az containerapp env create \
        --name $ENVIRONMENT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $RG_LOCATION
    echo -e "${GREEN}✓ Container Apps Environment created${NC}"
fi

# Prompt for API keys
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}API Configuration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Please provide your API keys:"
read -p "Google API Key (or press Enter to use default): " GOOGLE_API_KEY
read -p "Google Search Engine ID (or press Enter to use default): " SEARCH_ENGINE_ID
read -p "OpenAI API Key (optional, press Enter to skip): " OPENAI_API_KEY

# Use defaults if not provided
GOOGLE_API_KEY=${GOOGLE_API_KEY:-"AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E"}
SEARCH_ENGINE_ID=${SEARCH_ENGINE_ID:-"f080b786cd52e44c4"}

# Deploy Container App
echo ""
echo "Deploying Container App..."

# Check if app exists
if az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Updating existing Container App..."
    
    UPDATE_CMD="az containerapp update \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --image ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG} \
        --set-env-vars \
            GOOGLE_API_KEY=${GOOGLE_API_KEY} \
            SEARCH_ENGINE_ID=${SEARCH_ENGINE_ID} \
            PORT=5001"
    
    if [ ! -z "$OPENAI_API_KEY" ]; then
        UPDATE_CMD="$UPDATE_CMD OPENAI_API_KEY=${OPENAI_API_KEY}"
    fi
    
    eval $UPDATE_CMD
    
else
    echo "Creating new Container App..."
    
    CREATE_CMD="az containerapp create \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $ENVIRONMENT_NAME \
        --image ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG} \
        --registry-server ${ACR_LOGIN_SERVER} \
        --registry-username ${ACR_USERNAME} \
        --registry-password ${ACR_PASSWORD} \
        --target-port 5001 \
        --ingress external \
        --cpu 1.0 \
        --memory 2.0Gi \
        --min-replicas 1 \
        --max-replicas 3 \
        --env-vars \
            GOOGLE_API_KEY=${GOOGLE_API_KEY} \
            SEARCH_ENGINE_ID=${SEARCH_ENGINE_ID} \
            PORT=5001"
    
    if [ ! -z "$OPENAI_API_KEY" ]; then
        CREATE_CMD="$CREATE_CMD OPENAI_API_KEY=${OPENAI_API_KEY}"
    fi
    
    eval $CREATE_CMD
fi

echo -e "${GREEN}✓ Container App deployed${NC}"

# Get the app URL
echo ""
echo "Getting application URL..."
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Application URL:${NC}"
echo -e "https://${APP_URL}"
echo ""
echo -e "${BLUE}API Endpoints:${NC}"
echo -e "Health Check: https://${APP_URL}/api/health"
echo -e "Complete Search: https://${APP_URL}/api/complete"
echo ""
echo -e "${BLUE}Web Interface:${NC}"
echo -e "Chat Interface: https://${APP_URL}/web-chat/index.html"
echo ""
echo -e "${GREEN}Deployment successful!${NC}"
