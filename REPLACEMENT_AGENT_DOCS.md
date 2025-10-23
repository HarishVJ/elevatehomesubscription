# Replacement Search Agent Documentation

## Overview

The **Replacement Search Agent** finds comparable appliance replacements from multiple retail websites based on original product specifications.

## Purpose

Takes output from **Product Research Agent** and searches across major retailers (Home Depot, Lowe's, Best Buy, P.C. Richard & Son) to find matching replacement products.

## How It Works

```
Input (from Product Research Agent)
    ↓
Search Multiple Retailers
    ↓
Extract Product Data
    ↓
Calculate Match Scores
    ↓
Rank & Return Top 10
```

## Installation

Already included in the same environment:
```bash
pip install -r requirements.txt
```

## Basic Usage

### Standalone Usage

```python
from replacement_search_agent import ReplacementSearchAgent

# Initialize agent
agent = ReplacementSearchAgent(
    google_api_key="YOUR_GOOGLE_API_KEY",
    search_engine_id="YOUR_SEARCH_ENGINE_ID"
)

# Original product spec
original_product = {
    "brand": "GE",
    "model": "JGB735",
    "type": "range",
    "size": "30 inch",
    "fuel": "gas",
    "features": ["convection", "air fry", "self cleaning", "5 burners"]
}

# Search for replacements
result = agent.search(original_product)

# Check results
if result.success:
    print(f"Found {len(result.replacements)} replacements")
    for match in result.replacements:
        print(f"{match.rank}. {match.product_name}")
        print(f"   Score: {match.match_score}, Price: ${match.price}")
```

### Integrated with Product Research Agent

```python
from product_research_agent import ProductResearchAgent
from replacement_search_agent import ReplacementSearchAgent

# Step 1: Research original product
research_agent = ProductResearchAgent(
    api_key="google-key",
    search_engine_id="cx-id"
)

original = research_agent.research("GE", "JGB735", "range")

# Step 2: Find replacements
replacement_agent = ReplacementSearchAgent(
    google_api_key="google-key",
    search_engine_id="cx-id"
)

# Convert to spec format
product_spec = {
    "brand": "GE",
    "model": "JGB735",
    "type": original.product.type,
    "size": original.product.size,
    "fuel": original.product.fuel,
    "features": original.product.features
}

replacements = replacement_agent.search(product_spec)

# Display results
for match in replacements.replacements:
    print(f"{match.rank}. {match.product_name} - ${match.price}")
    print(f"   Match Score: {match.match_score}/100")
    print(f"   Retailer: {match.retailer}")
    print(f"   URL: {match.url}")
```

## Input Format

The agent expects a product specification dictionary:

```python
{
    "brand": "GE",              # Original brand
    "model": "JGB735",          # Original model
    "type": "range",            # Appliance type
    "size": "30 inch",          # Size with units
    "fuel": "gas",              # Fuel type
    "features": [               # List of features
        "convection",
        "air fry",
        "self cleaning"
    ]
}
```

## Output Format

```python
{
    "success": True,
    "search_summary": {
        "retailers_searched": 4,
        "total_products_found": 25,
        "viable_matches": 10
    },
    "original_product": {
        "brand": "GE",
        "model": "JGB735",
        "type": "range",
        "size": "30 inch",
        "fuel": "gas",
        "features": ["convection", "air fry"]
    },
    "replacements": [
        {
            "rank": 1,
            "product_name": "Samsung 30\" Gas Range with Convection",
            "brand": "Samsung",
            "model": "NX60A6711SS",
            "price": 1099.00,
            "size": "30 inch",
            "fuel": "gas",
            "features": ["convection", "air fry", "5 burners"],
            "url": "https://www.homedepot.com/p/...",
            "retailer": "Home Depot",
            "availability": "in stock",
            "match_score": 125,
            "match_details": {
                "size_match": True,
                "fuel_match": True,
                "features_matched": ["convection", "air fry"],
                "features_missing": ["self cleaning"],
                "price_competitive": True
            }
        },
        ...
    ]
}
```

## Retailers Searched

1. **Home Depot** (homedepot.com)
2. **Lowe's** (lowes.com)
3. **Best Buy** (bestbuy.com)
4. **P.C. Richard & Son** (pcrichard.com)

## Matching Algorithm

### Critical Criteria (Must Match)

1. **Appliance Type**: Exact match required
   - Mismatch = Disqualified

2. **Size**: Within ±2 inches tolerance
   - Exact match: +20 points
   - Within ±1 inch: +15 points
   - Within ±2 inches: +10 points
   - Beyond ±2 inches: -50 points (disqualified)

3. **Fuel Type**: Must match exactly
   - Match: +20 points
   - Mismatch: -50 points (disqualified)

### Feature Scoring

- **Each matched feature**: +10 points
- **Each missing required feature**: -15 points

### Availability & Price

- **In stock**: +10 points
- **Limited stock**: +5 points
- **Unknown**: +3 points
- **Price available**: +5 points

### Scoring Formula

```
Base Score: 100 points

Final Score = Base 
            + Type Match (10)
            + Size Match (0-20)
            + Fuel Match (20)
            + Features Matched (10 each)
            - Features Missing (15 each)
            + Availability (0-10)
            + Price Available (5)

Minimum Viable Score: 60 points
```

### Example Scoring

**Original**: 30" gas range, convection, air fry, self-cleaning

**Match 1**: 30" gas range, convection, air fry, 5 burners
```
Base: 100
Type: +10
Size (exact): +20
Fuel (gas): +20
Features matched (2): +20
Features missing (1): -15
In stock: +10
Price: +5
---
Total: 170 points ✓
```

**Match 2**: 30" electric range, convection
```
Base: 100
Type: +10
Size (exact): +20
Fuel (electric ≠ gas): -50
Features matched (1): +10
Features missing (2): -30
---
Total: 60 points (barely viable)
```

## Ranking Logic

Products are sorted by:

1. **Match Score** (descending - highest first)
2. **Price** (ascending - lowest first)
3. **Availability** (in stock first)

Top 10 products are returned.

## Data Extraction

The agent extracts from search results:

### Product Name
- Full product title from search result

### Brand
- Detected from common brands: GE, Whirlpool, LG, Samsung, etc.

### Model Number
- Alphanumeric patterns (e.g., "JGB735SPSS")

### Price
- Patterns: $1,299, $1299.99, 1299
- Handles sale prices
- Returns null if not found

### Size
- Ranges/Dishwashers/Microwaves: "30 inch", "24 inch"
- Refrigerators: "25 cubic feet" or "30 inch"

### Fuel Type
- Detected: gas, electric, dual
- Returns null if not mentioned

### Features
- Keywords: convection, air fry, self-cleaning, wifi, smart, etc.
- Burner count: "5 burners"
- Returns array of matched features

### Availability
- "in stock" - explicitly available
- "limited stock" - limited availability
- "out of stock" - unavailable
- "unknown" - not mentioned

## Error Handling

### No Products Found
```python
{
    "success": True,
    "search_summary": {
        "retailers_searched": 4,
        "total_products_found": 0,
        "viable_matches": 0
    },
    "replacements": [],
    "message": "No matching products found..."
}
```

### All Below Threshold
```python
{
    "success": True,
    "search_summary": {
        "retailers_searched": 4,
        "total_products_found": 15,
        "viable_matches": 0
    },
    "replacements": [],
    "message": "Products found but none meet minimum match criteria..."
}
```

### Search API Error
```python
{
    "success": False,
    "error": "Google Search API error: ...",
    "replacements": []
}
```

## Cost

Same as Product Research Agent:
- **~$0.001 per retailer searched**
- **4 retailers = ~$0.004 per search**
- **No AI costs** (rule-based extraction only)

## Performance

- **Speed**: 3-6 seconds (searches 4 retailers)
- **Results**: Up to 10 products per search
- **Accuracy**: Depends on search result quality

## Limitations

1. **Data Quality**: Depends on search result snippets
2. **Price Accuracy**: May not reflect current prices
3. **Availability**: Based on snippet text, may be outdated
4. **No Web Scraping**: Doesn't visit actual product pages
5. **Feature Detection**: Limited to mentioned features

## Best Practices

### 1. Use Complete Specifications
```python
# Good
product_spec = {
    "type": "range",
    "size": "30 inch",
    "fuel": "gas",
    "features": ["convection", "air fry", "self cleaning"]
}

# Less effective
product_spec = {
    "type": "range",
    "size": "30 inch",
    "features": []
}
```

### 2. Handle Missing Data
```python
result = agent.search(product_spec)

for match in result.replacements:
    price = match.price if match.price else "Price not available"
    print(f"{match.product_name}: {price}")
```

### 3. Check Match Details
```python
for match in result.replacements:
    if match.match_details['features_missing']:
        print(f"Missing: {match.match_details['features_missing']}")
```

### 4. Filter by Availability
```python
in_stock = [m for m in result.replacements if m.availability == 'in stock']
```

### 5. Set Price Limits
```python
affordable = [m for m in result.replacements if m.price and m.price < 1500]
```

## Integration Example

Complete workflow from research to replacement:

```python
from product_research_agent import ProductResearchAgent
from replacement_search_agent import ReplacementSearchAgent

# Initialize both agents
research = ProductResearchAgent(
    api_key="google-key",
    search_engine_id="cx-id"
)

replacement = ReplacementSearchAgent(
    google_api_key="google-key",
    search_engine_id="cx-id"
)

# Step 1: Research original product
print("Researching original product...")
original = research.research("GE", "JGB735", "range")

if not original.success:
    print(f"Error: {original.error}")
    exit(1)

print(f"Found: {original.product.size} {original.product.fuel} {original.product.type}")
print(f"Features: {', '.join(original.product.features[:3])}")

# Step 2: Find replacements
print("\nSearching for replacements...")
product_spec = {
    "brand": "GE",
    "model": "JGB735",
    "type": original.product.type,
    "size": original.product.size,
    "fuel": original.product.fuel,
    "features": original.product.features
}

replacements = replacement.search(product_spec)

# Step 3: Display results
print(f"\nFound {len(replacements.replacements)} replacements:")
print(f"Searched {replacements.search_summary['retailers_searched']} retailers")
print()

for match in replacements.replacements[:5]:  # Top 5
    print(f"{match.rank}. {match.product_name}")
    print(f"   Price: ${match.price if match.price else 'N/A'}")
    print(f"   Score: {match.match_score}/100")
    print(f"   Retailer: {match.retailer}")
    print(f"   Features: {', '.join(match.features[:3])}")
    print(f"   URL: {match.url}")
    print()
```

## Troubleshooting

### No Results Found
- Check internet connection
- Verify API keys
- Try broader search criteria (fewer features)

### Low Match Scores
- Original specs may be too specific
- Try removing optional features
- Check if size/fuel are correct

### Missing Prices
- Normal - not all search results show prices
- Visit product URL for current price
- Filter results with prices: `[m for m in results if m.price]`

### Wrong Products Returned
- Refine original specifications
- Add more specific features
- Check retailer search results manually

## API Reference

### ReplacementSearchAgent

#### `__init__(google_api_key, search_engine_id)`
Initialize the agent with API credentials.

#### `search(product_spec) -> SearchResult`
Search for replacement products.

**Args:**
- `product_spec` (dict): Product specifications

**Returns:**
- `SearchResult` object with replacements

#### `search_json(product_spec) -> str`
Search and return JSON string.

**Args:**
- `product_spec` (dict): Product specifications

**Returns:**
- JSON string

### Data Classes

#### ProductMatch
- `rank`: Ranking position (1-10)
- `product_name`: Full product name
- `brand`: Manufacturer brand
- `model`: Model number (or null)
- `price`: Price in dollars (or null)
- `size`: Size with units
- `fuel`: Fuel type
- `features`: List of features
- `url`: Product page URL
- `retailer`: Retailer name
- `availability`: Stock status
- `match_score`: Match score (0-200+)
- `match_details`: Detailed match information

#### SearchResult
- `success`: Operation success status
- `search_summary`: Search statistics
- `original_product`: Original product specs
- `replacements`: List of ProductMatch objects
- `message`: Optional message
- `error`: Optional error message

## Future Enhancements

Potential improvements:

1. **Web Scraping**: Visit actual product pages for accurate data
2. **More Retailers**: Add Amazon, Costco, etc.
3. **Price Tracking**: Monitor price changes
4. **AI Enhancement**: Use LLM for better extraction
5. **Image Matching**: Compare product images
6. **Review Analysis**: Include customer ratings
7. **Caching**: Store search results
8. **Batch Processing**: Search multiple products at once

## Support

For issues:
1. Check API keys are valid
2. Verify internet connection
3. Review search results manually
4. Check retailer websites are accessible
5. Ensure product specs are complete

## Version

**Version**: 1.0.0
**Status**: Production Ready
**Dependencies**: requests (same as Product Research Agent)
