# Project Overview

## Two-Agent System for Appliance Research & Replacement

### 1. Product Research Agent
**Purpose**: Extract appliance specifications from web search results

**Input**: Brand, Model, Appliance Type  
**Output**: Size, Fuel, Features, Source, Confidence

**File**: `product_research_agent.py`  
**Docs**: `README.md`

### 2. Replacement Search Agent
**Purpose**: Find comparable replacement products from retailers

**Input**: Product specifications (from Research Agent)  
**Output**: Top 10 matching products from 4 retailers

**File**: `replacement_search_agent.py`  
**Docs**: `REPLACEMENT_AGENT_DOCS.md`

---

## Quick Start

### Install
```bash
pip install -r requirements.txt
```

### Test Product Research
```bash
python3 example.py
```

### Test Replacement Search
```bash
python3 example_replacement.py
```

### Run Tests
```bash
python3 test_agent.py
```

---

## Complete Workflow

```python
from product_research_agent import ProductResearchAgent
from replacement_search_agent import ReplacementSearchAgent

# Step 1: Research original product
research = ProductResearchAgent("google-key", "cx-id")
original = research.research("GE", "JGB735", "range")

# Step 2: Find replacements
replacement = ReplacementSearchAgent("google-key", "cx-id")
spec = {
    "brand": "GE",
    "model": "JGB735",
    "type": original.product.type,
    "size": original.product.size,
    "fuel": original.product.fuel,
    "features": original.product.features
}
replacements = replacement.search(spec)

# Step 3: Display results
for match in replacements.replacements[:5]:
    print(f"{match.product_name} - ${match.price}")
```

---

## Files

### Core (2 files)
- `product_research_agent.py` - Product research agent
- `replacement_search_agent.py` - Replacement search agent

### Documentation (3 files)
- `README.md` - Product Research Agent docs
- `REPLACEMENT_AGENT_DOCS.md` - Replacement Agent docs
- `QUICK_REFERENCE.md` - Quick reference guide
- `PROJECT_OVERVIEW.md` - This file

### Examples (3 files)
- `example.py` - Basic research examples
- `example_ai.py` - AI features demo
- `example_replacement.py` - Complete workflow

### Testing & Config (3 files)
- `test_agent.py` - Test suite
- `requirements.txt` - Dependencies
- `.gitignore` - Git ignore rules

**Total**: 11 files

---

## Documentation

- **Product Research Agent**: See `README.md`
- **Replacement Search Agent**: See `REPLACEMENT_AGENT_DOCS.md`
- **Quick Commands**: See `QUICK_REFERENCE.md`

---

## Status

✅ Both agents production-ready  
✅ All tests passing  
✅ Complete documentation  
✅ Working examples
