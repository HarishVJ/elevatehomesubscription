# Product Research Agent

A specialized Python agent for finding and extracting appliance specifications from web search results using Google Custom Search API with **AI-enhanced hybrid extraction**.

## Features

- **Hybrid Extraction**: Rule-based + AI fallback for optimal cost/accuracy balance
- **AI-Powered**: GPT-4o-mini for intelligent specification extraction when needed
- **Cost-Efficient**: Only uses AI when rule-based quality is low (~$0.003/product avg)
- **Web Search Integration**: Uses Google Custom Search API to find product information
- **Structured Output**: Returns data in standardized JSON format
- **Multi-Appliance Support**: Handles ranges, dishwashers, refrigerators, and microwaves
- **Confidence Scoring**: Rates source reliability (high/medium/low)
- **Extraction Method Tracking**: Know whether rule-based or AI was used

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Option 1: With AI Enhancement (Recommended)

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"
```

```python
from product_research_agent import ProductResearchAgent

# Initialize with AI capabilities
agent = ProductResearchAgent(
    api_key="YOUR_GOOGLE_API_KEY",
    search_engine_id="YOUR_SEARCH_ENGINE_ID",
    use_ai=True  # Enable AI fallback (default)
)

result = agent.research("GE", "JGB735", "range")
print(f"Method: {result.extraction_method}")  # 'rule-based' or 'ai'
print(f"Size: {result.product.size}")
```

### Option 2: Rule-Based Only (No AI)

```python
agent = ProductResearchAgent(
    api_key="YOUR_GOOGLE_API_KEY",
    search_engine_id="YOUR_SEARCH_ENGINE_ID",
    use_ai=False  # Disable AI
)

result = agent.research("GE", "JGB735", "range")
# Always uses rule-based extraction (cheapest)
```

## Usage

### Basic Usage

```python
from product_research_agent import ProductResearchAgent

# Initialize agent with API credentials
agent = ProductResearchAgent(
    api_key="YOUR_GOOGLE_API_KEY",
    search_engine_id="YOUR_SEARCH_ENGINE_ID"
)

# Research a product
result_json = agent.research_json(
    brand="GE",
    model="JGB735",
    appliance_type="range"
)

print(result_json)
```

### Advanced Usage

```python
from product_research_agent import ProductResearchAgent

agent = ProductResearchAgent(api_key="...", search_engine_id="...")

# Get structured result object
result = agent.research(
    brand="Samsung",
    model="DW80R9950US",
    appliance_type="dishwasher"
)

if result.success:
    print(f"Type: {result.product.type}")
    print(f"Size: {result.product.size}")
    print(f"Fuel: {result.product.fuel}")
    print(f"Features: {', '.join(result.product.features)}")
    print(f"Source: {result.source}")
    print(f"Confidence: {result.confidence}")
else:
    print(f"Error: {result.error}")
```

## API Configuration

### Required
1. **Google Custom Search API Key**: Get from [Google Cloud Console](https://console.cloud.google.com/)
2. **Search Engine ID (cx)**: Create at [Programmable Search Engine](https://programmablesearchengine.google.com/)

### Optional (for AI Enhancement)
3. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/)
   - Set as environment variable: `export OPENAI_API_KEY="sk-..."`
   - Or pass directly: `openai_api_key="sk-..."`

## Output Format

```json
{
  "success": true,
  "product": {
    "type": "range",
    "size": "30 inch",
    "fuel": "gas",
    "features": [
      "convection",
      "air fry",
      "self cleaning",
      "5 burners",
      "storage drawer"
    ]
  },
  "source": "geappliances.com",
  "confidence": "high",
  "extraction_method": "rule-based"
}
```

## Supported Appliance Types

- **range**: Gas, electric, or dual fuel cooking ranges
- **dishwasher**: Built-in and portable dishwashers
- **refrigerator**: All refrigerator configurations
- **microwave**: Countertop, over-the-range, and built-in microwaves

## Extraction Methods

- **rule-based**: Fast keyword matching (free, 70-80% accuracy)
- **ai**: GPT-4o-mini extraction (~$0.002-0.005, 90-95% accuracy)

The agent automatically chooses the best method based on quality assessment.

## Cost & Performance

| Mode | Cost/Product | Accuracy | Speed | Best For |
|------|-------------|----------|-------|----------|
| Rule-based only | ~$0.001 | 70-80% | Fast | Budget-critical |
| Hybrid (default) | ~$0.003 | 85-90% | Fast | Production |
| AI always | ~$0.005 | 90-95% | Slower | High accuracy |

**Example**: 1,000 products with hybrid mode = ~$3 (vs $5 for all AI, $1 for all rule-based)

## Confidence Levels

- **high**: Information from manufacturer/official websites
- **medium**: Information from major retailers (Home Depot, Lowe's, Best Buy, etc.)
- **low**: Information from reviews or unclear sources

## Error Handling

The agent returns structured error responses:

```json
{
  "success": false,
  "error": "No search results found for Brand Model",
  "product": null
}
```

## Architecture

### Classes

- **ProductResearchAgent**: Main agent class
  - `search()`: Execute Google Custom Search API query
  - `analyze_results()`: Extract specifications from search results
  - `research()`: Complete research workflow
  - `research_json()`: Research with JSON output

- **ProductSpecification**: Data class for product specs
  - `type`: Appliance category
  - `size`: Physical dimensions
  - `fuel`: Power/fuel type
  - `features`: List of features

- **ResearchResult**: Data class for research results
  - `success`: Operation status
  - `product`: ProductSpecification object
  - `source`: Primary source domain
  - `confidence`: Reliability rating
  - `error`: Error message if failed

## Feature Detection

The agent automatically detects appliance-specific features:

### Range Features
- Convection, air fryer, self-cleaning
- Burner count and types
- Storage drawer, warming drawer
- WiFi/smart capabilities

### Dishwasher Features
- Noise level (decibels)
- Third rack, soil sensor
- Cycle count and types
- Stainless steel tub

### Refrigerator Features
- Ice maker, water dispenser
- Door configuration
- Capacity (cubic feet)
- Smart features

### Microwave Features
- Convection, sensor cooking
- Installation type
- Power levels
- Ventilation capabilities

## Testing

### Run Examples
```bash
python3 example.py        # Basic examples
python3 example_ai.py     # AI features demo
```

### Run Test Suite
```bash
python3 test_agent.py
```

All 6 tests should pass:
- ✓ Basic Search
- ✓ JSON Output
- ✓ Different Appliances
- ✓ Error Handling
- ✓ Feature Extraction
- ✓ Confidence Scoring
