#!/bin/bash

# Deploy Web Chat as Static Website in Azure Storage

set -e

echo "================================================"
echo "Static Website Deployment"
echo "================================================"
echo ""

# Configuration
RESOURCE_GROUP="rg-containerappssriparag"
STORAGE_ACCOUNT="elevatewebchat$(date +%s)"
LOCATION="eastus"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found"
    exit 1
fi
echo "✅ Azure CLI found"

# Check login
if ! az account show &> /dev/null; then
    echo "Logging in..."
    az login
fi
echo "✅ Logged in to Azure"

# Create storage account
echo ""
echo "Creating storage account: $STORAGE_ACCOUNT"
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --kind StorageV2 \
    --output none

echo "✅ Storage account created"

# Enable static website
echo ""
echo "Enabling static website..."
az storage blob service-properties update \
    --account-name $STORAGE_ACCOUNT \
    --static-website \
    --index-document index.html \
    --404-document index.html \
    --output none

echo "✅ Static website enabled"

# Upload files
echo ""
echo "Uploading web chat files..."
az storage blob upload-batch \
    --account-name $STORAGE_ACCOUNT \
    --source ./web-chat \
    --destination '$web' \
    --overwrite \
    --output none

echo "✅ Files uploaded"

# Get the URL
echo ""
WEBSITE_URL=$(az storage account show \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query "primaryEndpoints.web" \
    --output tsv)

echo "================================================"
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "================================================"
echo ""
echo "🌐 Static Website URL:"
echo "   $WEBSITE_URL"
echo ""
echo "🔗 Direct Links:"
echo "   Main Interface: ${WEBSITE_URL}"
echo "   Test Page: ${WEBSITE_URL}test.html"
echo ""
echo "📊 Storage Account: $STORAGE_ACCOUNT"
echo "📁 Resource Group: $RESOURCE_GROUP"
echo ""
echo "🧪 Test the API connection:"
echo "   Open: ${WEBSITE_URL}test.html"
echo ""
echo "================================================"
