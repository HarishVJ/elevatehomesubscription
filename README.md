# Elevate Home Subscription - Appliance Research Agent System

A comprehensive AI-powered agent system for finding appliance specifications and replacement options using Google Custom Search API with **AI-enhanced hybrid extraction**.

## 🎯 Overview

This system consists of three specialized AI agents working together:

1. **Product Research Agent** - Finds and extracts original appliance specifications
2. **Replacement Search Agent** - Discovers comparable replacement products from retailers
3. **Chat Interface Agent** - Provides conversational user interface

## ✨ Features

- **Hybrid Extraction**: Rule-based + AI fallback for optimal cost/accuracy balance
- **AI-Powered**: GPT-4o-mini for intelligent specification extraction when needed
- **Multi-Retailer Search**: Searches Home Depot, Lowe's, Best Buy, P.C. Richard & Son
- **Smart Matching**: Intelligent scoring algorithm ranks replacements by compatibility
- **Web Interface**: Angular-based chat interface for easy user interaction
- **REST API**: Flask server with comprehensive endpoints
- **Cost-Efficient**: Only uses AI when rule-based quality is low (~$0.003/product avg)
- **Structured Output**: Returns data in standardized JSON format
- **Multi-Appliance Support**: Handles ranges, dishwashers, refrigerators, and microwaves

## 📚 Documentation

### Getting Started
- **[START_HERE.md](START_HERE.md)** - Quick start guide
- **[AGENTS_OVERVIEW.md](AGENTS_OVERVIEW.md)** - Detailed agent documentation
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command reference

### AI Agent Prompts (For External Systems)
- **[PRODUCT_RESEARCH_AGENT_PROMPT.md](PRODUCT_RESEARCH_AGENT_PROMPT.md)** - AI prompt for Product Research Agent
- **[CHAT_INTERFACE_AGENT_PROMPT.md](CHAT_INTERFACE_AGENT_PROMPT.md)** - AI prompt for Chat Interface Agent
- **[REPLACEMENT_AGENT_DOCS.md](REPLACEMENT_AGENT_DOCS.md)** - Replacement Search Agent documentation

### Technical Documentation
- **[AGENT_COMMUNICATION.md](AGENT_COMMUNICATION.md)** - How agents communicate
- **[SYSTEM_FLOW_DIAGRAM.md](SYSTEM_FLOW_DIAGRAM.md)** - Complete system architecture
- **[SCORING_ALGORITHM.md](SCORING_ALGORITHM.md)** - Replacement matching algorithm

### Deployment
- **[AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md)** - Azure Container Apps deployment
- **[STATIC_WEBSITE_DEPLOYMENT.md](STATIC_WEBSITE_DEPLOYMENT.md)** - Static website deployment
- **[WEB_INTERFACE_GUIDE.md](WEB_INTERFACE_GUIDE.md)** - Web interface setup

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Option 1: Complete Workflow (API Server)

```bash
# Start the API server
python3 api_server.py

# In another terminal, open the web interface
cd web-chat
open index.html
```

### Option 2: Python API Usage

```python
from product_research_agent import ProductResearchAgent
from replacement_search_agent import ReplacementSearchAgent

# Initialize agents
research_agent = ProductResearchAgent(
    api_key="YOUR_GOOGLE_API_KEY",
    search_engine_id="YOUR_SEARCH_ENGINE_ID",
    use_ai=True
)

replacement_agent = ReplacementSearchAgent(
    google_api_key="YOUR_GOOGLE_API_KEY",
    search_engine_id="YOUR_SEARCH_ENGINE_ID"
)

# Step 1: Research original product
result = research_agent.research("GE", "JGB735", "range")

# Step 2: Find replacements
if result.success:
    product_spec = {
        'type': result.product.type,
        'size': result.product.size,
        'fuel': result.product.fuel,
        'features': result.product.features
    }
    replacements = replacement_agent.search(product_spec)
    
    print(f"Found {len(replacements.replacements)} replacements")
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (Chat UI)      │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Flask API      │
│  (api_server)   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────────┐
│Product │ │Replacement │
│Research│ │Search Agent│
└────┬───┘ └──────┬─────┘
     │            │
     ▼            ▼
┌─────────────────────┐
│  Google Custom      │
│  Search API         │
└─────────────────────┘
```

## 📋 API Endpoints

### Health Check
```bash
GET /api/health
```

### Research Product
```bash
POST /api/research
{
  "brand": "GE",
  "model": "JGB735",
  "appliance_type": "range"
}
```

### Find Replacements
```bash
POST /api/replacements
{
  "brand": "GE",
  "model": "JGB735",
  "type": "range",
  "size": "30 inch",
  "fuel": "gas",
  "features": ["convection", "air fry"],
  "brand_for_brand": false,
  "dollar_limit": 2000
}
```

### Complete Workflow
```bash
POST /api/complete
{
  "brand": "GE",
  "model": "JGB735",
  "appliance_type": "range",
  "brand_for_brand": false,
  "dollar_limit": 2000
}
```

## 🔧 Configuration

### Required API Keys
1. **Google Custom Search API Key**: Get from [Google Cloud Console](https://console.cloud.google.com/)
2. **Search Engine ID (cx)**: Create at [Programmable Search Engine](https://programmablesearchengine.google.com/)

### Optional (for AI Enhancement)
3. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/)
   - Set as environment variable: `export OPENAI_API_KEY="sk-..."`

## 💰 Cost & Performance

| Component | Cost/Request | Time | Accuracy |
|-----------|-------------|------|----------|
| Product Research | ~$0.003 | 1-2s | 85-95% |
| Replacement Search | ~$0.028 | 2-4s | 90-95% |
| **Complete Workflow** | **~$0.03** | **5-10s** | **90%+** |

## 🧪 Testing

```bash
# Test agents directly
python3 test_agent.py

# Test API server
curl http://localhost:5000/api/health

# Run examples
python3 example.py
python3 example_ai.py
python3 example_replacement.py
```

## 📦 Project Structure

```
ElevatePOC/
├── product_research_agent.py       # Product Research Agent
├── replacement_search_agent.py     # Replacement Search Agent
├── api_server.py                   # Flask API server
├── web-chat/                       # Static web interface
├── web-chat-angular/               # Angular web interface
├── PRODUCT_RESEARCH_AGENT_PROMPT.md  # AI prompt for external systems
├── CHAT_INTERFACE_AGENT_PROMPT.md    # AI prompt for external systems
└── [Documentation files...]
```

## 🌟 Key Features

### Product Research Agent
✅ Hybrid extraction (rule-based + AI)  
✅ Confidence scoring  
✅ Multiple sources  
✅ Fallback methods  
✅ Structured output

### Replacement Search Agent
✅ Multi-retailer search (4 retailers)  
✅ Parallel processing  
✅ Smart scoring algorithm  
✅ Flexible filtering  
✅ Detailed matching

### Chat Interface Agent
✅ Conversational UI  
✅ Step-by-step guidance  
✅ Real-time search  
✅ Rich results display  
✅ Error handling

## 🚢 Deployment

### Local Development
```bash
python3 api_server.py
```

### Azure Container Apps
```bash
./azure-deploy.sh
```

### Static Website (Azure Storage)
```bash
./deploy-static-website.sh
```

## 📖 Support

- See [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) for common issues
- Check [AGENTS_OVERVIEW.md](AGENTS_OVERVIEW.md) for detailed documentation
- Review [SYSTEM_FLOW_DIAGRAM.md](SYSTEM_FLOW_DIAGRAM.md) for architecture

## 📄 License

This project is part of the Elevate Home Subscription system.

## 🤝 Contributing

For questions or contributions, please refer to the documentation files in this repository.
