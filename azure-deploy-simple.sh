#!/bin/bash

# Simple Azure Container App Deployment
# Uses existing resource group: rg-containerappssriparag
# Container app name: ssripaElevateapp

set -e

echo "========================================="
echo "Azure Container App Deployment"
echo "========================================="
echo ""

# Configuration
RESOURCE_GROUP="rg-containerappssriparag"
CONTAINER_APP_NAME="ssripaElevateapp"
ENVIRONMENT_NAME="${CONTAINER_APP_NAME}-env"
IMAGE="mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"  # Temporary, will be replaced

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI not installed"
    exit 1
fi

# Login check
if ! az account show &> /dev/null; then
    echo "Logging in to Azure..."
    az login
fi

echo "✓ Logged in to Azure"
echo ""

# Get resource group location
RG_LOCATION=$(az group show --name $RESOURCE_GROUP --query location -o tsv)
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $RG_LOCATION"
echo ""

# Create Container Apps Environment
echo "Creating Container Apps Environment..."
if ! az containerapp env show --name $ENVIRONMENT_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    az containerapp env create \
        --name $ENVIRONMENT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $RG_LOCATION
    echo "✓ Environment created"
else
    echo "✓ Environment already exists"
fi

echo ""
echo "Next steps:"
echo "1. Build Docker image locally"
echo "2. Push to Azure Container Registry"
echo "3. Deploy container app"
echo ""
echo "Run: ./azure-deploy.sh for full automated deployment"
