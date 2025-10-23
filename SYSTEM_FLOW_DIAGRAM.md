# System Flow Diagram

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                                │
│                    (Any Device, Any Location)                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTPS Request
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              AZURE STORAGE STATIC WEBSITE                            │
│         https://elevatewebchat1760713146.z13.web.core.windows.net   │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ index.html   │  │ styles.css   │  │   app.js     │             │
│  │ (UI Layout)  │  │ (Styling)    │  │ (Logic)      │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
│  Cost: ~$1-2/month                                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ API Calls (HTTPS + CORS)
                             │ POST /api/complete
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│           AZURE CONTAINER APP (API Backend)                          │
│    https://sspripaelevateapp.proudbush-0db0d62f.eastus...           │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Flask API Server                          │   │
│  │                    (api_server.py)                           │   │
│  │                                                              │   │
│  │  Endpoints:                                                  │   │
│  │  • GET  /api/health                                          │   │
│  │  • POST /api/complete                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                             │                                        │
│                             │ Calls                                  │
│                             ▼                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Product Research Agent                           │  │
│  │           (product_research_agent.py)                         │  │
│  │                                                               │  │
│  │  • Searches Google for product specs                          │  │
│  │  • Extracts: type, size, fuel, features                      │  │
│  │  • Uses hybrid (rule-based + AI) extraction                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                             │                                        │
│                             │ Product Specs                          │
│                             ▼                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           Replacement Search Agent                            │  │
│  │          (replacement_search_agent.py)                        │  │
│  │                                                               │  │
│  │  • Searches 4 retailers (Home Depot, Lowe's, etc.)           │  │
│  │  • Matches products by specs                                 │  │
│  │  • Calculates match scores (0-200+)                          │  │
│  │  • Ranks and filters results                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Resources: 1-3 replicas, 1.0 CPU, 2.0 GB RAM                      │
│  Cost: ~$10-25/month                                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ API Calls
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL APIs                                   │
│                                                                      │
│  ┌──────────────────────┐      ┌──────────────────────┐            │
│  │  Google Custom       │      │  OpenAI API          │            │
│  │  Search API          │      │  (Optional)          │            │
│  │                      │      │                      │            │
│  │  • Web search        │      │  • AI extraction     │            │
│  │  • Retailer results  │      │  • Feature parsing   │            │
│  └──────────────────────┘      └──────────────────────┘            │
│                                                                      │
│  Cost: ~$0.007 per search                                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete User Flow

### **Step-by-Step Process**

```
1. USER OPENS WEBSITE
   │
   ├─→ Browser loads: https://elevatewebchat1760713146.z13.web.core.windows.net/
   │
   └─→ Static files served from Azure Storage:
       • index.html (UI structure)
       • styles.css (styling)
       • app.js (JavaScript logic)

2. USER INTERACTS WITH CHAT INTERFACE
   │
   ├─→ Step 1: Select Appliance Type (range, dishwasher, etc.)
   ├─→ Step 2: Choose Brand (GE, Whirlpool, etc.)
   ├─→ Step 3: Enter Model Number (JGB735, etc.)
   ├─→ Step 4: Brand-for-Brand? (Yes/No)
   └─→ Step 5: Budget Limit (optional)

3. USER CLICKS "SEARCH NOW"
   │
   └─→ JavaScript (app.js) prepares API request:
       {
         "brand": "GE",
         "model": "JGB735",
         "appliance_type": "range",
         "brand_for_brand": false,
         "dollar_limit": null
       }

4. API REQUEST SENT
   │
   └─→ POST https://sspripaelevateapp.../api/complete
       • Method: POST
       • Headers: Content-Type: application/json
       • Body: JSON request data
       • CORS: Enabled

5. CONTAINER APP RECEIVES REQUEST
   │
   └─→ Flask API Server (api_server.py)
       • Validates request
       • Extracts parameters
       • Calls Product Research Agent

6. PRODUCT RESEARCH PHASE
   │
   ├─→ Product Research Agent (product_research_agent.py)
   │   │
   │   ├─→ Constructs search query: "GE JGB735 range specifications"
   │   │
   │   ├─→ Calls Google Custom Search API
   │   │   • Searches manufacturer sites
   │   │   • Searches retailer sites
   │   │   • Returns top 10 results
   │   │
   │   ├─→ Extracts product specifications:
   │   │   • Type: range
   │   │   • Size: 30 inch
   │   │   • Fuel: gas
   │   │   • Features: [convection, air fry, wifi, ...]
   │   │
   │   └─→ Returns ProductResult:
   │       {
   │         "success": true,
   │         "product": {...},
   │         "confidence": "high",
   │         "extraction_method": "rule-based"
   │       }
   │
   └─→ Duration: 1-2 seconds

7. REPLACEMENT SEARCH PHASE
   │
   ├─→ Replacement Search Agent (replacement_search_agent.py)
   │   │
   │   ├─→ Searches 4 retailers in parallel:
   │   │   • Home Depot (homedepot.com)
   │   │   • Lowe's (lowes.com)
   │   │   • Best Buy (bestbuy.com)
   │   │   • P.C. Richard & Son (pcrichard.com)
   │   │
   │   ├─→ For each retailer:
   │   │   • Constructs query: "site:homedepot.com 30 inch gas range"
   │   │   • Calls Google Custom Search API
   │   │   • Extracts product details
   │   │   • Parses price, features, availability
   │   │
   │   ├─→ Calculates match scores:
   │   │   • Base score: 100
   │   │   • Type match: +10
   │   │   • Size match: +20 (exact) or +15 (±1") or +10 (±2")
   │   │   • Fuel match: +20
   │   │   • Each feature matched: +10
   │   │   • Each feature missing: -15
   │   │   • Availability bonus: +10 (in stock)
   │   │   • Price info bonus: +5
   │   │
   │   ├─→ Filters results:
   │   │   • Minimum score: 60
   │   │   • Brand filter (if brand-for-brand)
   │   │   • Price filter (if dollar limit set)
   │   │
   │   └─→ Ranks and returns top 10
   │
   └─→ Duration: 2-4 seconds

8. API RESPONSE PREPARED
   │
   └─→ Flask combines results:
       {
         "success": true,
         "original_product": {
           "brand": "GE",
           "model": "JGB735",
           "type": "range",
           "size": "30 inch",
           "fuel": "gas",
           "features": [...],
           "confidence": "high"
         },
         "replacements": [
           {
             "rank": 1,
             "product_name": "Samsung 30\" Gas Range...",
             "brand": "Samsung",
             "price": 1099.00,
             "match_score": 190,
             "retailer": "Home Depot",
             "url": "https://..."
           },
           ... (9 more)
         ],
         "search_summary": {
           "total_searched": 40,
           "viable_matches": 15,
           "returned": 10
         }
       }

9. RESPONSE SENT TO BROWSER
   │
   └─→ HTTP 200 OK
       • Content-Type: application/json
       • CORS headers included
       • Total time: 5-10 seconds

10. JAVASCRIPT DISPLAYS RESULTS
    │
    ├─→ Original Product Card:
    │   • Shows type, size, fuel, features
    │   • Displays confidence level
    │   • Shows source URL
    │
    └─→ Replacement Product Cards (10):
        • Ranked by match score
        • Shows product name, brand, price
        • Displays match score and details
        • Shows retailer and availability
        • Provides direct product link

11. USER VIEWS RESULTS
    │
    └─→ Can click product links to purchase
        Can start new search
        Can adjust filters
```

---

## 📊 Data Flow Diagram

```
┌──────────┐
│  User    │
│  Input   │
└────┬─────┘
     │
     │ {brand, model, type, filters}
     ▼
┌─────────────────┐
│  Static Website │
│   (Frontend)    │
└────┬────────────┘
     │
     │ HTTP POST /api/complete
     │ {brand, model, appliance_type, brand_for_brand, dollar_limit}
     ▼
┌─────────────────────────┐
│   Flask API Server      │
│   (api_server.py)       │
└────┬────────────────────┘
     │
     │ research(brand, model, type)
     ▼
┌─────────────────────────────────┐
│  Product Research Agent         │
│  (product_research_agent.py)    │
└────┬────────────────────────────┘
     │
     │ Google Search Query
     ▼
┌─────────────────────────┐
│  Google Custom Search   │
│  API                    │
└────┬────────────────────┘
     │
     │ Search Results (HTML snippets)
     ▼
┌─────────────────────────────────┐
│  Specification Extraction       │
│  (Hybrid: Rules + AI)           │
└────┬────────────────────────────┘
     │
     │ {type, size, fuel, features}
     ▼
┌─────────────────────────────────┐
│  Replacement Search Agent       │
│  (replacement_search_agent.py)  │
└────┬────────────────────────────┘
     │
     │ 4 Parallel Searches (one per retailer)
     ▼
┌─────────────────────────┐
│  Google Custom Search   │
│  API (4x calls)         │
└────┬────────────────────┘
     │
     │ Product listings from retailers
     ▼
┌─────────────────────────────────┐
│  Product Matching & Scoring     │
│  (Score calculation algorithm)  │
└────┬────────────────────────────┘
     │
     │ Scored & ranked products
     ▼
┌─────────────────────────────────┐
│  Filtering & Ranking            │
│  (Brand, price, score filters)  │
└────┬────────────────────────────┘
     │
     │ Top 10 replacements
     ▼
┌─────────────────────────┐
│  Flask API Response     │
└────┬────────────────────┘
     │
     │ JSON Response
     ▼
┌─────────────────────────┐
│  Static Website         │
│  (Display Results)      │
└────┬────────────────────┘
     │
     │ Rendered HTML
     ▼
┌──────────┐
│  User    │
│  Views   │
└──────────┘
```

---

## 🔀 Scoring Algorithm Flow

```
START: Product from retailer search
  │
  ├─→ Initialize: score = 100
  │
  ├─→ CHECK: Type Match?
  │   ├─→ YES: score += 10
  │   └─→ NO: DISQUALIFY (score = 0, exit)
  │
  ├─→ CHECK: Size Match?
  │   ├─→ Exact (30" = 30"): score += 20
  │   ├─→ Close (29-31"): score += 15
  │   ├─→ Within tolerance (28-32"): score += 10
  │   └─→ Outside tolerance (>2" diff): score -= 50
  │
  ├─→ CHECK: Fuel Match?
  │   ├─→ Same (gas = gas): score += 20
  │   ├─→ Different (gas ≠ electric): score -= 50
  │   └─→ N/A (dishwasher): no change
  │
  ├─→ CHECK: Features
  │   ├─→ For each matched feature: score += 10
  │   └─→ For each missing feature: score -= 15
  │
  ├─→ CHECK: Availability
  │   ├─→ In stock: score += 10
  │   ├─→ Limited stock: score += 5
  │   └─→ Unknown: score += 3
  │
  ├─→ CHECK: Has price?
  │   └─→ YES: score += 5
  │
  ├─→ FILTER: score >= 60?
  │   ├─→ YES: Keep product
  │   └─→ NO: Discard product
  │
  └─→ RANK: Sort by score (highest first)
      │
      └─→ Return top 10
```

---

## 🌐 Network Flow

```
User Browser
    │
    │ 1. HTTPS GET
    ▼
Azure Storage (Static Website)
    │
    │ 2. Returns HTML/CSS/JS
    ▼
User Browser (Executes JavaScript)
    │
    │ 3. HTTPS POST /api/complete
    │    Origin: https://elevatewebchat...
    │    Content-Type: application/json
    ▼
Azure Container App
    │
    │ 4. CORS Check (Allow Origin)
    │ 5. Process Request
    │
    ├─→ 6. HTTPS GET (Google Search)
    │   └─→ Google API
    │       └─→ Returns search results
    │
    ├─→ 7. HTTPS POST (OpenAI - optional)
    │   └─→ OpenAI API
    │       └─→ Returns extracted data
    │
    └─→ 8. HTTPS GET (Google Search x4)
        └─→ Google API (4 retailer searches)
            └─→ Returns product listings
    │
    │ 9. Combine & format response
    ▼
User Browser
    │
    │ 10. Display results
    ▼
User sees products
```

---

## ⏱️ Timing Breakdown

```
Total Time: 5-10 seconds

┌─────────────────────────────────────────────────┐
│ Phase 1: Product Research (1-2 sec)            │
│ ├─ Google Search: 0.5-1 sec                    │
│ ├─ HTML parsing: 0.2-0.5 sec                   │
│ └─ Spec extraction: 0.3-0.5 sec                │
├─────────────────────────────────────────────────┤
│ Phase 2: Replacement Search (2-4 sec)          │
│ ├─ 4 Google searches (parallel): 1-2 sec       │
│ ├─ Product extraction: 0.5-1 sec               │
│ └─ Scoring & ranking: 0.5-1 sec                │
├─────────────────────────────────────────────────┤
│ Phase 3: Response formatting (0.1-0.2 sec)     │
├─────────────────────────────────────────────────┤
│ Network latency: 0.5-1 sec                     │
└─────────────────────────────────────────────────┘
```

---

## 💾 Data Storage Flow

```
┌─────────────────────────────────────────────────┐
│         NO PERSISTENT STORAGE                   │
│                                                 │
│  All data is:                                   │
│  • Fetched in real-time                         │
│  • Processed on-the-fly                         │
│  • Returned immediately                         │
│  • Not stored                                   │
│                                                 │
│  Benefits:                                      │
│  • Always fresh data                            │
│  • No database costs                            │
│  • No data privacy concerns                     │
│  • Stateless architecture                       │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Error Handling Flow

```
Request Received
    │
    ├─→ Validate Input
    │   ├─→ Valid → Continue
    │   └─→ Invalid → Return 400 Error
    │
    ├─→ Product Research
    │   ├─→ Success → Continue
    │   └─→ Failure → Return error message
    │
    ├─→ Replacement Search
    │   ├─→ Success → Continue
    │   └─→ Partial failure → Return available results
    │
    └─→ Return Response
        ├─→ Success: 200 OK
        └─→ Error: 400/500 with error message
```

---

This comprehensive flow diagram shows how all components work together from user input to final results display! 🚀
