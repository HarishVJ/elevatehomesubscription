# Static Website Deployment Guide

## Overview

Deploy the web chat interface as a static website in Azure Storage Account. The static site will call your Container App API.

**Architecture**:
```
User Browser → Azure Storage (Static Website) → Azure Container App (API)
```

---

## 📦 Static Files Ready

The `web-chat/` folder contains all files needed:
- `index.html` - Main page
- `styles.css` - Styling
- `app.js` - JavaScript (configured for your API)
- `test.html` - Test page

**API URL configured**: `https://sspripaelevateapp.proudbush-0db0d62f.eastus.azurecontainerapps.io/api`

---

## 🚀 Deployment Steps

### Option 1: Azure Portal (GUI)

#### Step 1: Create Storage Account

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"** → **"Storage account"**
3. Fill in:
   - **Resource Group**: `rg-containerappssriparag`
   - **Storage account name**: `elevatewebchat` (must be globally unique, lowercase)
   - **Region**: `East US`
   - **Performance**: Standard
   - **Redundancy**: LRS (cheapest)
4. Click **"Review + Create"** → **"Create"**

#### Step 2: Enable Static Website

1. Open your storage account
2. In left menu, go to **"Static website"** (under Data management)
3. Click **"Enabled"**
4. Set:
   - **Index document name**: `index.html`
   - **Error document path**: `index.html`
5. Click **"Save"**
6. Copy the **Primary endpoint URL** (e.g., `https://elevatewebchat.z13.web.core.windows.net/`)

#### Step 3: Upload Files

1. In storage account, go to **"Storage browser"** → **"Blob containers"**
2. Click on **"$web"** container
3. Click **"Upload"**
4. Upload these files from `web-chat/` folder:
   - `index.html`
   - `styles.css`
   - `app.js`
   - `test.html` (optional)
5. Click **"Upload"**

#### Step 4: Test

Open the Primary endpoint URL in your browser:
```
https://elevatewebchat.z13.web.core.windows.net/
```

---

### Option 2: Azure CLI (Command Line)

```bash
# Set variables
RESOURCE_GROUP="rg-containerappssriparag"
STORAGE_ACCOUNT="elevatewebchat$(date +%s)"  # Unique name
LOCATION="eastus"

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2

# Enable static website
az storage blob service-properties update \
  --account-name $STORAGE_ACCOUNT \
  --static-website \
  --index-document index.html \
  --404-document index.html

# Upload files
az storage blob upload-batch \
  --account-name $STORAGE_ACCOUNT \
  --source ./web-chat \
  --destination '$web' \
  --overwrite

# Get the URL
az storage account show \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query "primaryEndpoints.web" \
  --output tsv
```

---

### Option 3: Automated Script

I'll create a script for you:

```bash
chmod +x deploy-static-website.sh
./deploy-static-website.sh
```

---

## 🔧 Configuration

### API URL

The web chat is already configured to use your Container App API:
```javascript
const API_BASE_URL = 'https://sspripaelevateapp.proudbush-0db0d62f.eastus.azurecontainerapps.io/api';
```

### CORS

Your Container App API already has CORS enabled via Flask-CORS, so the static website can call it.

---

## 📊 File Structure

```
web-chat/
├── index.html          # Main chat interface
├── styles.css          # Responsive styling
├── app.js              # JavaScript with API calls
└── test.html           # API connection test page
```

**Total size**: ~50 KB (very small!)

---

## 💰 Cost

**Azure Storage Static Website**:
- Storage: ~$0.02/GB/month
- Bandwidth: First 5 GB free, then ~$0.087/GB
- **Estimated**: ~$1-2/month for typical usage

**Total System Cost**:
- Container App: ~$10-25/month
- Static Website: ~$1-2/month
- **Total**: ~$11-27/month

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain

1. In Storage Account, go to **"Custom domain"**
2. Enter your domain: `chat.yourdomain.com`
3. Add CNAME record in your DNS:
   ```
   chat.yourdomain.com → elevatewebchat.z13.web.core.windows.net
   ```
4. Click **"Save"**

### Enable HTTPS with Azure CDN

1. Create Azure CDN profile
2. Add CDN endpoint pointing to storage account
3. Enable HTTPS
4. Map custom domain to CDN

---

## 🧪 Testing

### Test API Connection

1. Open: `https://your-storage-url.web.core.windows.net/test.html`
2. Click **"Test Health Check"** → Should show Status 200
3. Click **"Test Complete Search"** → Should return results

### Test Main Interface

1. Open: `https://your-storage-url.web.core.windows.net/`
2. Try a search:
   - Appliance: Range
   - Brand: GE
   - Model: JGB735
   - Click "Search Now"
3. Should see results in 5-10 seconds

---

## 🐛 Troubleshooting

### CORS Error

If you see CORS errors in browser console:

**Check Container App CORS**:
```bash
# CORS should already be enabled, but verify
az containerapp show \
  --name sspripaelevateapp \
  --resource-group rg-containerappssriparag \
  --query properties.configuration.ingress.corsPolicy
```

**Fix if needed**: Update `api_server.py` to ensure CORS is enabled:
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### 404 Not Found

- Verify files uploaded to `$web` container
- Check file names are exact: `index.html`, `styles.css`, `app.js`
- Ensure static website is enabled

### API Not Responding

```bash
# Test API directly
curl https://sspripaelevateapp.proudbush-0db0d62f.eastus.azurecontainerapps.io/api/health
```

---

## 📈 Performance

### Optimization Tips

1. **Enable CDN**: Add Azure CDN for faster global access
2. **Compress files**: Enable gzip compression
3. **Cache headers**: Set cache-control headers
4. **Minify**: Minify CSS and JS (optional)

### Current Performance

- **Load time**: <1 second
- **API response**: 5-10 seconds (search)
- **Total size**: ~50 KB

---

## 🔄 Updates

### Update Static Website

When you make changes to web-chat files:

**Via Portal**:
1. Go to Storage Account → Storage browser → $web
2. Delete old files
3. Upload new files

**Via CLI**:
```bash
az storage blob upload-batch \
  --account-name $STORAGE_ACCOUNT \
  --source ./web-chat \
  --destination '$web' \
  --overwrite
```

---

## 📋 Deployment Checklist

Before deployment:
- [ ] Container App API is running
- [ ] API health check returns 200
- [ ] web-chat/app.js has correct API URL
- [ ] Storage account created
- [ ] Static website enabled

After deployment:
- [ ] Static website URL accessible
- [ ] test.html shows successful API connection
- [ ] Main interface loads
- [ ] Search functionality works
- [ ] Results display correctly

---

## 🎯 Quick Commands

### Create and Deploy

```bash
# Create storage account
STORAGE_ACCOUNT="elevatewebchat$(date +%s)"
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group rg-containerappssriparag \
  --location eastus \
  --sku Standard_LRS

# Enable static website
az storage blob service-properties update \
  --account-name $STORAGE_ACCOUNT \
  --static-website \
  --index-document index.html

# Upload files
az storage blob upload-batch \
  --account-name $STORAGE_ACCOUNT \
  --source ./web-chat \
  --destination '$web'

# Get URL
az storage account show \
  --name $STORAGE_ACCOUNT \
  --resource-group rg-containerappssriparag \
  --query "primaryEndpoints.web" \
  -o tsv
```

---

## ✅ Ready to Deploy!

Your static files are ready in the `web-chat/` folder with the API URL already configured.

**Next Steps**:
1. Create storage account
2. Enable static website
3. Upload the 3 files (index.html, styles.css, app.js)
4. Access your static website URL

**That's it!** 🚀
