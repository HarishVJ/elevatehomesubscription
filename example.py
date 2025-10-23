"""
Example usage of the Product Research Agent
"""

from product_research_agent import ProductResearchAgent
import json


def main():
    # Initialize agent with API credentials
    API_KEY = "AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E"
    SEARCH_ENGINE_ID = "f080b786cd52e44c4"
    
    agent = ProductResearchAgent(API_KEY, SEARCH_ENGINE_ID)
    
    # Example 1: Research a GE range
    print("=" * 60)
    print("Example 1: GE Range")
    print("=" * 60)
    
    result = agent.research(
        brand="GE",
        model="JGB735",
        appliance_type="range"
    )
    
    if result.success:
        print(f"✓ Success!")
        print(f"  Type: {result.product.type}")
        print(f"  Size: {result.product.size}")
        print(f"  Fuel: {result.product.fuel}")
        print(f"  Features: {', '.join(result.product.features)}")
        print(f"  Source: {result.source}")
        print(f"  Confidence: {result.confidence}")
    else:
        print(f"✗ Error: {result.error}")
    
    print()
    
    # Example 2: Research with JSON output
    print("=" * 60)
    print("Example 2: JSON Output")
    print("=" * 60)
    
    result_json = agent.research_json(
        brand="Samsung",
        model="RF28R7351SR",
        appliance_type="refrigerator"
    )
    
    print(result_json)
    print()
    
    # Example 3: Handle product not found
    print("=" * 60)
    print("Example 3: Product Not Found")
    print("=" * 60)
    
    result = agent.research(
        brand="FakeBrand",
        model="NOTREAL123",
        appliance_type="dishwasher"
    )
    
    if result.success:
        print(f"✓ Success!")
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"✗ Error: {result.error}")
    
    print()
    
    # Example 4: Multiple products
    print("=" * 60)
    print("Example 4: Batch Research")
    print("=" * 60)
    
    products = [
        {"brand": "Whirlpool", "model": "WFG505M0BS", "type": "range"},
        {"brand": "LG", "model": "LDT7808SS", "type": "dishwasher"},
        {"brand": "Bosch", "model": "HMV8053U", "type": "microwave"}
    ]
    
    for product in products:
        result = agent.research(
            brand=product["brand"],
            model=product["model"],
            appliance_type=product["type"]
        )
        
        if result.success:
            print(f"✓ {product['brand']} {product['model']}")
            print(f"  Size: {result.product.size or 'N/A'}")
            print(f"  Features: {len(result.product.features)} found")
            print(f"  Confidence: {result.confidence}")
        else:
            print(f"✗ {product['brand']} {product['model']}: {result.error}")
        print()


if __name__ == "__main__":
    main()
