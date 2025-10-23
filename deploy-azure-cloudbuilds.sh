#!/bin/bash

# Azure Container Apps Deployment - Cloud Build (No Docker Required)
# Builds container image in Azure Cloud Build

set -e

echo "================================================"
echo "Azure Container Apps - Cloud Build Deployment"
echo "================================================"
echo ""
echo "Resource Group: rg-containerappssriparag"
echo "Container App: ssripaElevateapp"
echo "No Docker required - builds in Azure!"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Install from: https://aka.ms/InstallAzureCLIDeb"
    exit 1
fi
echo "✅ Azure CLI found"

# Check Azure login
echo ""
echo "Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "Please login to Azure:"
    az login
fi

SUBSCRIPTION=$(az account show --query name -o tsv)
echo "✅ Logged in to: $SUBSCRIPTION"

# Configuration
RESOURCE_GROUP="rg-containerappssriparag"
CONTAINER_APP_NAME="ssripaElevateapp"
ACR_NAME="acrelevateapp$(date +%s)"
ENVIRONMENT_NAME="${CONTAINER_APP_NAME}-env"

# Verify resource group
echo ""
echo "Verifying resource group..."
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "❌ Resource group '$RESOURCE_GROUP' not found"
    exit 1
fi

RG_LOCATION=$(az group show --name $RESOURCE_GROUP --query location -o tsv)
echo "✅ Resource group found in: $RG_LOCATION"

# Create ACR
echo ""
echo "Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --location $RG_LOCATION \
    --admin-enabled true \
    --output none

ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
echo "✅ ACR created: $ACR_LOGIN_SERVER"

# Build image in Azure (no local Docker needed!)
echo ""
echo "Building image in Azure Cloud Build..."
echo "This may take 2-3 minutes..."
az acr build \
    --registry $ACR_NAME \
    --image elevate-app:latest \
    --file Dockerfile \
    . \
    --output table

echo "✅ Image built in Azure"

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Create Container Apps Environment
echo ""
echo "Creating Container Apps Environment..."
if az containerapp env show --name $ENVIRONMENT_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "✅ Environment already exists"
else
    az containerapp env create \
        --name $ENVIRONMENT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $RG_LOCATION \
        --output none
    echo "✅ Environment created"
fi

# Deploy Container App
echo ""
echo "Deploying Container App..."

GOOGLE_API_KEY="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E"
SEARCH_ENGINE_ID="f080b786cd52e44c4"

if az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Updating existing app..."
    az containerapp update \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --image ${ACR_LOGIN_SERVER}/elevate-app:latest \
        --set-env-vars \
            GOOGLE_API_KEY=${GOOGLE_API_KEY} \
            SEARCH_ENGINE_ID=${SEARCH_ENGINE_ID} \
            PORT=5001 \
        --output none
else
    echo "Creating new app..."
    az containerapp create \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $ENVIRONMENT_NAME \
        --image ${ACR_LOGIN_SERVER}/elevate-app:latest \
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
            PORT=5001 \
        --output none
fi

echo "✅ Container App deployed"

# Get application URL
echo ""
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo "================================================"
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "================================================"
echo ""
echo "🌐 Application URL:"
echo "   https://${APP_URL}"
echo ""
echo "🔍 API Endpoints:"
echo "   Health: https://${APP_URL}/api/health"
echo "   Search: https://${APP_URL}/api/complete"
echo ""
echo "💬 Web Interface:"
echo "   https://${APP_URL}/web-chat/index.html"
echo ""
echo "📊 View logs:"
echo "   az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "================================================"
