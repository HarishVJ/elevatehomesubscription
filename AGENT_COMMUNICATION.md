# Agent Communication Architecture

## 🔄 How Agents Communicate

---

## 1️⃣ **Agent-to-Agent Communication**

### **Direct Function Calls (Synchronous)**

The agents communicate through **direct Python function calls** within the same Flask application process.

```python
# In api_server.py

# Step 1: Initialize both agents
research_agent = ProductResearchAgent(
    api_key=GOOGLE_API_KEY,
    search_engine_id=SEARCH_ENGINE_ID,
    use_ai=True
)

replacement_agent = ReplacementSearchAgent(
    google_api_key=GOOGLE_API_KEY,
    search_engine_id=SEARCH_ENGINE_ID
)

# Step 2: Call Product Research Agent
research_result = research_agent.research(brand, model, appliance_type)

# Step 3: Extract product specs from result
product_spec = {
    'brand': brand,
    'model': model,
    'type': research_result.product.type,
    'size': research_result.product.size,
    'fuel': research_result.product.fuel,
    'features': research_result.product.features
}

# Step 4: Pass specs to Replacement Search Agent
replacement_result = replacement_agent.search(product_spec)
```

### **Communication Flow**

```
Flask API Server (api_server.py)
    │
    ├─→ Creates ProductResearchAgent instance
    ├─→ Creates ReplacementSearchAgent instance
    │
    └─→ When /api/complete is called:
        │
        ├─→ 1. Calls research_agent.research()
        │   │
        │   └─→ Returns: ProductResult object
        │       {
        │         success: bool,
        │         product: ProductSpecification,
        │         source: str,
        │         confidence: str
        │       }
        │
        └─→ 2. Calls replacement_agent.search()
            │   (passes product specs from step 1)
            │
            └─→ Returns: SearchResult object
                {
                  success: bool,
                  replacements: List[ProductMatch],
                  search_summary: dict
                }
```

---

## 2️⃣ **Agent-to-External API Communication**

### **Product Research Agent → Google Custom Search API**

```python
# In product_research_agent.py

def _search_google(self, query: str) -> List[Dict]:
    """Search Google Custom Search API"""
    
    # HTTP GET request to Google API
    response = requests.get(
        self.api_endpoint,  # https://www.googleapis.com/customsearch/v1
        params={
            'key': self.api_key,           # Google API key
            'cx': self.search_engine_id,   # Search engine ID
            'q': query,                    # Search query
            'num': 10                      # Number of results
        }
    )
    
    # Returns JSON response
    return response.json()
```

**Communication Details**:
- **Protocol**: HTTPS (REST API)
- **Method**: GET
- **Format**: JSON
- **Authentication**: API Key in query parameter
- **Rate Limit**: 100 queries/day (free tier)
- **Response Time**: 0.5-1 second

---

### **Product Research Agent → OpenAI API (Optional)**

```python
# In product_research_agent.py

def _extract_with_ai(self, search_results: List[Dict]) -> ProductSpecification:
    """Extract specs using OpenAI API"""
    
    from openai import OpenAI
    
    client = OpenAI(api_key=self.openai_api_key)
    
    # HTTP POST request to OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract appliance specifications..."
            },
            {
                "role": "user",
                "content": f"Search results: {search_results}"
            }
        ],
        response_format={"type": "json_object"}
    )
    
    # Parse JSON response
    return json.loads(response.choices[0].message.content)
```

**Communication Details**:
- **Protocol**: HTTPS (REST API)
- **Method**: POST
- **Format**: JSON
- **Authentication**: Bearer token (API Key in header)
- **Rate Limit**: Varies by tier
- **Response Time**: 1-3 seconds
- **Cost**: ~$0.003 per request

---

### **Replacement Search Agent → Google Custom Search API**

```python
# In replacement_search_agent.py

def _search_retailer(self, retailer_domain: str, product_spec: Dict) -> List[Dict]:
    """Search a specific retailer"""
    
    # Construct query
    query = f"site:{retailer_domain} {product_spec['type']} {product_spec['size']}"
    
    # HTTP GET request to Google API
    response = requests.get(
        self.api_endpoint,
        params={
            'key': self.google_api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': 10
        }
    )
    
    return response.json()
```

**Communication Details**:
- **Protocol**: HTTPS (REST API)
- **Method**: GET
- **Format**: JSON
- **Parallel Requests**: 4 (one per retailer)
- **Response Time**: 1-2 seconds (parallel)

---

## 3️⃣ **Frontend-to-Backend Communication**

### **Static Website → Container App API**

```javascript
// In web-chat/app.js

async function searchProducts() {
    // Prepare request data
    const requestData = {
        brand: state.data.brand,
        model: state.data.model,
        appliance_type: state.data.appliance_type,
        brand_for_brand: state.data.brand_for_brand,
        dollar_limit: state.data.dollar_limit
    };
    
    // HTTP POST request to Container App API
    const response = await fetch(
        'https://sspripaelevateapp.../api/complete',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        }
    );
    
    // Parse JSON response
    const data = await response.json();
    
    // Display results
    displayResults(data);
}
```

**Communication Details**:
- **Protocol**: HTTPS (REST API)
- **Method**: POST
- **Format**: JSON
- **CORS**: Enabled (allows cross-origin requests)
- **Authentication**: None (public API)
- **Response Time**: 5-10 seconds

---

## 📊 **Complete Communication Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER BROWSER                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS POST (JSON)
                         │ {brand, model, type, ...}
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              FLASK API SERVER (api_server.py)                    │
│                                                                  │
│  @app.route('/api/complete', methods=['POST'])                  │
│  def complete_workflow():                                       │
│      data = request.json  ← Receives JSON                       │
│                                                                  │
│      # Agent 1: Product Research                                │
│      result1 = research_agent.research(...)  ← Function call    │
│                                                                  │
│      # Agent 2: Replacement Search                              │
│      result2 = replacement_agent.search(...)  ← Function call   │
│                                                                  │
│      return jsonify(response)  → Returns JSON                   │
└────────┬────────────────────────────┬───────────────────────────┘
         │                            │
         │ In-Process                 │ In-Process
         │ Function Call              │ Function Call
         ▼                            ▼
┌──────────────────────┐    ┌──────────────────────────┐
│ ProductResearchAgent │    │ ReplacementSearchAgent   │
│                      │    │                          │
│ research()           │    │ search()                 │
│   ↓                  │    │   ↓                      │
│ _search_google()     │    │ _search_retailer() x4    │
│   ↓                  │    │   ↓                      │
│ _extract_specs()     │    │ _calculate_match_score() │
└──────┬───────────────┘    └──────┬───────────────────┘
       │                            │
       │ HTTPS GET                  │ HTTPS GET (x4)
       ▼                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE CUSTOM SEARCH API                      │
│                                                                  │
│  GET /customsearch/v1?key=...&cx=...&q=...                      │
│                                                                  │
│  Returns JSON:                                                  │
│  {                                                              │
│    "items": [                                                   │
│      {                                                          │
│        "title": "...",                                          │
│        "link": "...",                                           │
│        "snippet": "..."                                         │
│      }                                                          │
│    ]                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
       │
       │ (Optional) HTTPS POST
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       OPENAI API                                 │
│                                                                  │
│  POST /v1/chat/completions                                      │
│  Authorization: Bearer sk-...                                   │
│                                                                  │
│  Returns JSON:                                                  │
│  {                                                              │
│    "choices": [{                                                │
│      "message": {                                               │
│        "content": "{\"type\":\"range\", ...}"                   │
│      }                                                          │
│    }]                                                           │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 **Authentication & Security**

### **API Keys Storage**

```python
# In api_server.py

# Environment variables (secure)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'default-key')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID', 'default-cx')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)

# Passed to agents
research_agent = ProductResearchAgent(
    api_key=GOOGLE_API_KEY,        # Not exposed to frontend
    search_engine_id=SEARCH_ENGINE_ID,
    openai_api_key=OPENAI_API_KEY  # Optional
)
```

**Security Model**:
```
Frontend (Public)
    ↓ No API keys exposed
Backend (Private)
    ↓ API keys in environment variables
External APIs
```

---

## 📡 **Communication Protocols**

### **1. In-Process Communication**

**Type**: Direct Python function calls  
**Speed**: Microseconds  
**Format**: Python objects (dataclasses)  
**Error Handling**: Try/catch blocks

```python
# Synchronous call
result = agent.research(brand, model, type)

# Returns Python object
if result.success:
    specs = result.product  # ProductSpecification object
```

---

### **2. HTTP REST API Communication**

**Type**: HTTPS requests  
**Speed**: 0.5-3 seconds per request  
**Format**: JSON  
**Error Handling**: HTTP status codes + error messages

```python
# Example: Google API call
response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
else:
    raise Exception(f"API error: {response.status_code}")
```

---

## 🔄 **Data Format Transformations**

### **Frontend → Backend**

```javascript
// JavaScript object
const request = {
    brand: "GE",
    model: "JGB735",
    appliance_type: "range"
};

// Serialized to JSON
const json = JSON.stringify(request);

// Sent via HTTP
fetch(url, { body: json })
```

### **Backend → Agent**

```python
# JSON from request
data = request.json

# Python dict
{
    'brand': 'GE',
    'model': 'JGB735',
    'appliance_type': 'range'
}

# Passed as function arguments
result = agent.research(
    brand=data['brand'],
    model=data['model'],
    appliance_type=data['appliance_type']
)
```

### **Agent → External API**

```python
# Python dict to query params
params = {
    'key': api_key,
    'cx': search_engine_id,
    'q': 'GE JGB735 range'
}

# HTTP GET with params
response = requests.get(url, params=params)

# JSON response to Python dict
data = response.json()
```

### **Agent → Agent**

```python
# ProductResearchAgent returns dataclass
@dataclass
class ProductSpecification:
    type: str
    size: str
    fuel: str
    features: List[str]

# ReplacementSearchAgent receives dict
product_spec = {
    'type': result.product.type,
    'size': result.product.size,
    'fuel': result.product.fuel,
    'features': result.product.features
}

replacement_result = replacement_agent.search(product_spec)
```

---

## ⚡ **Parallel vs Sequential Communication**

### **Sequential (Product Research)**

```python
# Step 1: Search Google
search_results = _search_google(query)  # 0.5-1 sec

# Step 2: Extract specs (depends on step 1)
specs = _extract_specs(search_results)  # 0.5-1 sec

# Total: 1-2 seconds
```

### **Parallel (Replacement Search)**

```python
# All 4 retailers searched simultaneously
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(_search_retailer, 'homedepot.com', specs),
        executor.submit(_search_retailer, 'lowes.com', specs),
        executor.submit(_search_retailer, 'bestbuy.com', specs),
        executor.submit(_search_retailer, 'pcrichard.com', specs)
    ]
    
    results = [f.result() for f in futures]

# Total: ~1-2 seconds (not 4-8 seconds!)
```

---

## 🐛 **Error Communication**

### **Error Propagation**

```python
# Agent level
try:
    result = agent.research(brand, model, type)
    if not result.success:
        return jsonify({'success': False, 'error': result.error}), 400
except Exception as e:
    return jsonify({'success': False, 'error': str(e)}), 500

# Frontend receives
{
    "success": false,
    "error": "Product not found"
}
```

---

## 📊 **Communication Summary**

| From | To | Protocol | Format | Speed | Type |
|------|----|---------:|--------|-------|------|
| Browser | API Server | HTTPS | JSON | 5-10s | Async |
| API Server | Research Agent | Function Call | Python Objects | <1ms | Sync |
| API Server | Replacement Agent | Function Call | Python Objects | <1ms | Sync |
| Research Agent | Google API | HTTPS | JSON | 0.5-1s | Sync |
| Research Agent | OpenAI API | HTTPS | JSON | 1-3s | Sync |
| Replacement Agent | Google API | HTTPS | JSON | 1-2s | Parallel |
| API Server | Browser | HTTPS | JSON | <100ms | Async |

---

## 🎯 **Key Takeaways**

1. **Agents are NOT microservices** - They run in the same process
2. **Communication is via function calls** - Not HTTP/REST between agents
3. **External APIs use HTTPS** - Standard REST API calls
4. **Data flows through Python objects** - Converted to/from JSON at boundaries
5. **Parallel processing** - Used for retailer searches to save time
6. **Stateless** - No database, all data in memory during request
7. **Synchronous flow** - Each step waits for previous to complete

This architecture is **simple, fast, and cost-effective** for the use case! 🚀
