# Quick Reference Guide

## Installation

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key"  # Optional, for AI features
```

## Basic Usage

```python
from product_research_agent import ProductResearchAgent

# Initialize
agent = ProductResearchAgent(
    api_key="google-api-key",
    search_engine_id="cx-id"
)

# Research a product
result = agent.research("GE", "JGB735", "range")

# Check result
if result.success:
    print(f"Size: {result.product.size}")
    print(f"Features: {result.product.features}")
    print(f"Method: {result.extraction_method}")
```

## Modes

### Hybrid (Default) - Recommended
```python
agent = ProductResearchAgent(..., use_ai=True)
result = agent.research("Brand", "Model", "type")
# Cost: ~$0.003, Accuracy: 85-90%
```

### Rule-Based Only - Cheapest
```python
agent = ProductResearchAgent(..., use_ai=False)
result = agent.research("Brand", "Model", "type")
# Cost: ~$0.001, Accuracy: 70-80%
```

### AI Always - Most Accurate
```python
agent = ProductResearchAgent(..., use_ai=True)
result = agent.research("Brand", "Model", "type", force_ai=True)
# Cost: ~$0.005, Accuracy: 90-95%
```

## Appliance Types

- `"range"` - Gas/electric cooking ranges
- `"dishwasher"` - Dishwashers
- `"refrigerator"` - Refrigerators
- `"microwave"` - Microwaves

## Output Structure

```python
result.success          # bool
result.product.type     # str
result.product.size     # str or None
result.product.fuel     # str or None
result.product.features # list[str]
result.source           # str (domain)
result.confidence       # "high" | "medium" | "low"
result.extraction_method # "rule-based" | "ai"
result.error            # str or None (if failed)
```

## Cost Comparison

| Mode | Per Product | 1,000 Products |
|------|------------|----------------|
| Rule-based | $0.001 | $1.00 |
| Hybrid | $0.003 | $3.00 |
| AI always | $0.005 | $5.00 |

## Common Patterns

### Batch Processing
```python
products = [
    {"brand": "GE", "model": "JGB735", "type": "range"},
    {"brand": "LG", "model": "LDT7808SS", "type": "dishwasher"},
]

for product in products:
    result = agent.research(**product)
    if result.success:
        print(f"{product['brand']}: {result.extraction_method}")
```

### Error Handling
```python
result = agent.research("Brand", "Model", "type")

if not result.success:
    print(f"Error: {result.error}")
else:
    # Process result
    pass
```

### JSON Output
```python
result_json = agent.research_json("GE", "JGB735", "range")
print(result_json)  # Pretty-printed JSON string
```

## Testing

```bash
# Run test suite
python3 test_agent.py

# Run examples
python3 example.py        # Basic examples
python3 example_ai.py     # AI examples

# Quick test
python3 product_research_agent.py
```

## Troubleshooting

### No AI extraction
- Check `OPENAI_API_KEY` is set
- Verify OpenAI account has credits
- Try `force_ai=True` to test

### Poor accuracy
- Enable AI: `use_ai=True`
- Use full model numbers
- Check search results manually

### High costs
- Disable AI: `use_ai=False`
- Implement caching
- Use batch processing

## Files

- `product_research_agent.py` - Main agent
- `example.py` - Basic examples
- `example_ai.py` - AI examples
- `test_agent.py` - Test suite
- `README.md` - Full documentation
- `SETUP_AI.md` - AI setup guide
- `ARCHITECTURE.md` - System architecture
- `TESTING.md` - Testing guide

## API Keys

### Required
- Google Custom Search API Key
- Search Engine ID (cx)

### Optional
- OpenAI API Key (for AI features)

### Setup
```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."  # Optional
export SEARCH_ENGINE_ID="..."    # Optional
```

## Support

For detailed information:
- Setup: `SETUP_AI.md`
- Architecture: `ARCHITECTURE.md`
- Testing: `TESTING.md`
- Full docs: `README.md`
