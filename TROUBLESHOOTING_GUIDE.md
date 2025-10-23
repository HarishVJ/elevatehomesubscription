# Troubleshooting Guide

## 🔍 Current Status

✅ **Google API Key**: Working (AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E)  
✅ **API Server**: Running on port 5001  
✅ **API Endpoint**: Tested and working (returns results in 2-3 seconds)  
⚠️ **Web Interface**: May have connection issues

---

## 🧪 Test Pages Available

### **1. Connection Test Page**
```
http://localhost:8000/test.html
```

This page will:
- Test API health check
- Test complete search workflow
- Show detailed logs and timing
- Display any connection errors

**Click the buttons to test:**
- "Test Health Check" - Quick API ping
- "Test Complete Search" - Full search with GE JGB735

---

### **2. Main Chat Interface**
```
http://localhost:8000/index.html
```

The main chat interface with full UI.

---

## 🐛 Debugging Steps

### **Step 1: Test API Connection**

Open: **http://localhost:8000/test.html**

1. Click **"Test Health Check"**
   - Should show: `Status: 200` and `{"status":"healthy",...}`
   - If fails: API server not running

2. Click **"Test Complete Search"**
   - Should show: `Status: 200` and results in 2-3 seconds
   - If fails: Check error message

---

### **Step 2: Check Browser Console**

1. Open main interface: **http://localhost:8000/index.html**
2. Open Developer Tools (F12 or Cmd+Option+I)
3. Go to **Console** tab
4. Try a search
5. Look for these logs:

**Expected (Success)**:
```
=== SEARCH STARTED ===
API URL: http://localhost:5001/api
Request data: {brand: "GE", model: "JGB735", ...}
Sending request to: http://localhost:5001/api/complete
Response status: 200
Response OK: true
Response data: {success: true, ...}
Success! Displaying results...
```

**Error Patterns**:
```
TypeError: Failed to fetch
→ API server not running or wrong port

CORS policy error
→ CORS not enabled (should be fixed)

Network error
→ Check API URL in app.js
```

---

### **Step 3: Check API Server Logs**

The API server should show logs like:

```
2025-10-16 XX:XX:XX - __main__ - INFO - Complete workflow request received
2025-10-16 XX:XX:XX - __main__ - INFO - Step 1: Researching product - GE JGB735
2025-10-16 XX:XX:XX - __main__ - INFO - Research result: success=True
2025-10-16 XX:XX:XX - __main__ - INFO - Product found: range, 30 inch, gas
2025-10-16 XX:XX:XX - __main__ - INFO - Step 2: Finding replacements
2025-10-16 XX:XX:XX - __main__ - INFO - Replacement search: found 10 products
2025-10-16 XX:XX:XX - __main__ - INFO - Sending response with 10 replacements
```

If you see nothing → Request not reaching server

---

## ✅ Verified Working

### **API Direct Test** (via curl)
```bash
curl -X POST http://localhost:5001/api/complete \
  -H "Content-Type: application/json" \
  -d '{"brand":"GE","model":"JGB735","appliance_type":"range","brand_for_brand":false,"dollar_limit":null}'
```

**Result**: ✅ Returns full JSON response in 2-3 seconds

### **Sample Response**:
```json
{
  "success": true,
  "original_product": {
    "brand": "GE",
    "model": "JGB735",
    "type": "range",
    "size": "30 inch",
    "fuel": "gas",
    "features": ["air fry", "convection", "smart", ...],
    "confidence": "high"
  },
  "replacements": [
    {
      "rank": 1,
      "product_name": "GE 30\" Gas Range...",
      "price": 1099.00,
      "match_score": 125,
      ...
    },
    ... (9 more)
  ]
}
```

---

## 🔧 Common Issues & Fixes

### **Issue 1: Infinite Spinner**

**Symptoms**: Search button clicked, spinner shows forever

**Possible Causes**:
1. API server not running
2. Wrong API URL in app.js
3. CORS blocking request
4. Network timeout

**Debug**:
1. Check browser console for errors
2. Test with test.html page
3. Verify API server is running: `curl http://localhost:5001/api/health`

---

### **Issue 2: "Connection Error"**

**Symptoms**: Error message appears immediately

**Cause**: Cannot connect to API server

**Fix**:
```bash
# Check if API server is running
lsof -i :5001

# If not running, start it
python3 run_api_debug.py
```

---

### **Issue 3: "No Results Found"**

**Symptoms**: Search completes but no replacements

**Possible Causes**:
1. Google API quota exceeded
2. Invalid model number
3. No matching products in retailers

**Debug**:
1. Check API server logs for errors
2. Try known working model: GE JGB735
3. Test Google API directly

---

### **Issue 4: CORS Error**

**Symptoms**: Browser console shows CORS policy error

**Fix**: Flask-CORS should be installed and enabled
```bash
pip install flask-cors
```

Already configured in `run_api_debug.py`:
```python
from flask_cors import CORS
CORS(app)
```

---

## 📊 Performance Expectations

### **Normal Timing**:
- Health check: <100ms
- Product research: 1-2 seconds
- Replacement search: 2-4 seconds
- **Total: 3-6 seconds**

### **If Slower**:
- 10+ seconds: Google API slow response
- 30+ seconds: Timeout likely
- Infinite: Connection issue

---

## 🎯 Test Inputs That Work

### **Test Case 1: GE Range** (Best)
```
Appliance: Range
Brand: GE
Model: JGB735
Brand-for-Brand: No
Budget: (empty)
```
**Expected**: 10 replacements in 3-6 seconds

### **Test Case 2: Simple Test**
```
Appliance: Range
Brand: Whirlpool
Model: WFG505M0BS
Brand-for-Brand: No
Budget: 1500
```
**Expected**: Filtered results under $1500

---

## 🚀 Quick Reset

If everything is broken, start fresh:

```bash
# 1. Kill all servers
pkill -f api_server
pkill -f http.server

# 2. Start API server
cd /Users/harish/learning/Harish/AgentAI/ElevatePOC
python3 run_api_debug.py &

# 3. Start web server
cd web-chat
python3 -m http.server 8000 &

# 4. Test
curl http://localhost:5001/api/health
curl http://localhost:8000/test.html
```

---

## 📝 Checklist

Before reporting issues, verify:

- [ ] API server running on port 5001
- [ ] Web server running on port 8000
- [ ] Can access http://localhost:8000/test.html
- [ ] Test page shows successful health check
- [ ] Test page shows successful search
- [ ] Browser console shows no CORS errors
- [ ] API server logs show request received

---

## 🆘 Still Not Working?

### **Try the test page first**:
```
http://localhost:8000/test.html
```

Click both buttons and share:
1. What the test page shows
2. Any error messages
3. Browser console logs
4. API server terminal output

This will help identify the exact issue!

---

## ✅ Success Indicators

You'll know it's working when:

1. **Test page** shows:
   - ✓ Health check: Status 200
   - ✓ Search: Status 200, results in 2-3 seconds

2. **Main interface** shows:
   - Original product card appears
   - 10 replacement cards appear
   - Each has price, score, retailer

3. **Browser console** shows:
   - No red errors
   - "Success! Displaying results..."

4. **API server** shows:
   - Request received logs
   - Research and replacement logs
   - Sending response logs

---

**Current Status**: API is working perfectly. If web interface has issues, use the test page to diagnose!
