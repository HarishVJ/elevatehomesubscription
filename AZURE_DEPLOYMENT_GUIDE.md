# Azure Container Apps Deployment Guide

## Overview

Deploy the Appliance Research System to Azure Container Apps using your existing resource group.

**Configuration**:
- Resource Group: `rg-containerappssriparag`
- Container App Name: `ssripaElevateapp`
- Region: Will use resource group's location

---

## Prerequisites

### 1. Azure CLI
```bash
# Check if installed
az --version

# If not installed, install from:
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
```

### 2. Docker
```bash
# Check if installed
docker --version

# If not installed, install Docker Desktop from:
# https://www.docker.com/products/docker-desktop
```

### 3. Azure Login
```bash
# Login to Azure
az login

# Verify subscription
az account show
```

---

## 🚀 Quick Deployment (Automated)

### Option 1: Full Automated Deployment

```bash
# Make script executable
chmod +x azure-deploy.sh

# Run deployment
./azure-deploy.sh
```

The script will:
1. ✅ Check Azure CLI and login status
2. ✅ Verify resource group exists
3. ✅ Create Azure Container Registry
4. ✅ Build Docker image
5. ✅ Push image to ACR
6. ✅ Create Container Apps Environment
7. ✅ Deploy Container App
8. ✅ Configure environment variables
9. ✅ Display application URL

**You'll be prompted for**:
- Google API Key (or use default)
- Search Engine ID (or use default)
- OpenAI API Key (optional)

---

## 📋 Manual Deployment (Step-by-Step)

### Step 1: Build Docker Image

```bash
# Build the image
docker build -t elevate-app:latest .

# Test locally (optional)
docker run -p 5001:5001 \
  -e GOOGLE_API_KEY="your-key" \
  -e SEARCH_ENGINE_ID="your-cx" \
  elevate-app:latest
```

### Step 2: Create Azure Container Registry

```bash
# Set variables
RESOURCE_GROUP="rg-containerappssriparag"
ACR_NAME="acrelevateapp"  # Must be globally unique

# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
echo $ACR_LOGIN_SERVER
```

### Step 3: Push Image to ACR

```bash
# Tag image
docker tag elevate-app:latest ${ACR_LOGIN_SERVER}/elevate-app:latest

# Login to ACR
az acr login --name $ACR_NAME

# Push image
docker push ${ACR_LOGIN_SERVER}/elevate-app:latest
```

### Step 4: Create Container Apps Environment

```bash
# Set variables
ENVIRONMENT_NAME="ssripaElevateapp-env"

# Get resource group location
RG_LOCATION=$(az group show --name $RESOURCE_GROUP --query location -o tsv)

# Create environment
az containerapp env create \
  --name $ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $RG_LOCATION
```

### Step 5: Deploy Container App

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Deploy container app
az containerapp create \
  --name ssripaElevateapp \
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
    GOOGLE_API_KEY="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E" \
    SEARCH_ENGINE_ID="f080b786cd52e44c4" \
    PORT=5001
```

### Step 6: Get Application URL

```bash
# Get the FQDN
az containerapp show \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv
```

---

## 🔧 Configuration

### Environment Variables

The container app uses these environment variables:

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GOOGLE_API_KEY` | Yes | Google Custom Search API key | - |
| `SEARCH_ENGINE_ID` | Yes | Google Search Engine ID (cx) | - |
| `OPENAI_API_KEY` | No | OpenAI API key for AI features | - |
| `PORT` | No | Port to run on | 5001 |
| `FLASK_DEBUG` | No | Enable debug mode | False |

### Update Environment Variables

```bash
az containerapp update \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    GOOGLE_API_KEY="new-key" \
    SEARCH_ENGINE_ID="new-cx"
```

---

## 📊 Resource Configuration

### Container Specs

```yaml
CPU: 1.0 cores
Memory: 2.0 GB
Min Replicas: 1
Max Replicas: 3
Port: 5001
Ingress: External (HTTPS)
```

### Scaling

The app auto-scales based on:
- HTTP requests
- CPU usage
- Memory usage

**Scale manually**:
```bash
az containerapp update \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 2 \
  --max-replicas 5
```

---

## 🔍 Monitoring & Logs

### View Logs

```bash
# Stream logs
az containerapp logs show \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --follow

# Get recent logs
az containerapp logs show \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --tail 100
```

### View Metrics

```bash
# Get revision info
az containerapp revision list \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --output table
```

### Health Check

```bash
# Get app URL
APP_URL=$(az containerapp show \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv)

# Test health endpoint
curl https://${APP_URL}/api/health
```

---

## 🔄 Update Deployment

### Update with New Image

```bash
# Build new image
docker build -t elevate-app:v2 .

# Tag and push
docker tag elevate-app:v2 ${ACR_LOGIN_SERVER}/elevate-app:v2
docker push ${ACR_LOGIN_SERVER}/elevate-app:v2

# Update container app
az containerapp update \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --image ${ACR_LOGIN_SERVER}/elevate-app:v2
```

### Rollback to Previous Version

```bash
# List revisions
az containerapp revision list \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --output table

# Activate previous revision
az containerapp revision activate \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --revision <revision-name>
```

---

## 🌐 Access the Application

Once deployed, access your application at:

```
Main URL: https://<your-app-fqdn>
```

### Endpoints

```
Health Check:
https://<your-app-fqdn>/api/health

Web Interface:
https://<your-app-fqdn>/web-chat/index.html

API Complete Search:
https://<your-app-fqdn>/api/complete
```

### Update Web Chat API URL

After deployment, update the web chat to use the Azure URL:

Edit `web-chat/app.js`:
```javascript
const API_BASE_URL = 'https://<your-app-fqdn>/api';
```

Then rebuild and redeploy.

---

## 💰 Cost Estimation

### Azure Container Apps Pricing

**Consumption Plan**:
- First 180,000 vCPU-seconds: Free
- First 360,000 GiB-seconds: Free
- After free tier: ~$0.000012/vCPU-second

**Estimated Monthly Cost**:
- Low usage (1000 requests/day): ~$5-10/month
- Medium usage (10000 requests/day): ~$20-40/month
- High usage (100000 requests/day): ~$100-200/month

**Additional Costs**:
- Azure Container Registry: ~$5/month (Basic tier)
- Bandwidth: Minimal for API responses

---

## 🔒 Security

### Secure API Keys

**Use Azure Key Vault** (Recommended):

```bash
# Create Key Vault
az keyvault create \
  --name elevate-keyvault \
  --resource-group $RESOURCE_GROUP \
  --location $RG_LOCATION

# Store secrets
az keyvault secret set \
  --vault-name elevate-keyvault \
  --name google-api-key \
  --value "your-key"

# Reference in Container App
az containerapp update \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --secrets \
    google-api-key=keyvaultref:https://elevate-keyvault.vault.azure.net/secrets/google-api-key,identityref:/subscriptions/.../managedIdentities/...
```

### Enable HTTPS Only

```bash
az containerapp ingress update \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --allow-insecure false
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
az containerapp logs show \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --tail 50

# Check revision status
az containerapp revision list \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP
```

### Image Pull Errors

```bash
# Verify ACR credentials
az acr credential show --name $ACR_NAME

# Test ACR access
az acr login --name $ACR_NAME
docker pull ${ACR_LOGIN_SERVER}/elevate-app:latest
```

### Application Errors

```bash
# Check environment variables
az containerapp show \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --query properties.template.containers[0].env

# Test locally with same env vars
docker run -p 5001:5001 \
  -e GOOGLE_API_KEY="your-key" \
  -e SEARCH_ENGINE_ID="your-cx" \
  elevate-app:latest
```

---

## 🗑️ Cleanup

### Delete Container App

```bash
az containerapp delete \
  --name ssripaElevateapp \
  --resource-group $RESOURCE_GROUP \
  --yes
```

### Delete Environment

```bash
az containerapp env delete \
  --name ssripaElevateapp-env \
  --resource-group $RESOURCE_GROUP \
  --yes
```

### Delete Container Registry

```bash
az acr delete \
  --name $ACR_NAME \
  --resource-group $RESOURCE_GROUP \
  --yes
```

---

## ✅ Deployment Checklist

Before deployment:
- [ ] Azure CLI installed and logged in
- [ ] Docker installed and running
- [ ] Resource group exists
- [ ] API keys ready (Google, OpenAI)
- [ ] Dockerfile tested locally

After deployment:
- [ ] Health check returns 200 OK
- [ ] Web interface loads
- [ ] Test search works
- [ ] Logs show no errors
- [ ] HTTPS enabled
- [ ] Environment variables set

---

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Azure Container Registry Documentation](https://docs.microsoft.com/en-us/azure/container-registry/)
- [Docker Documentation](https://docs.docker.com/)

---

## 🆘 Support

If you encounter issues:

1. Check logs: `az containerapp logs show ...`
2. Verify environment variables
3. Test Docker image locally
4. Check Azure service health
5. Review deployment script output

---

**Ready to deploy? Run `./azure-deploy.sh` to get started!** 🚀
