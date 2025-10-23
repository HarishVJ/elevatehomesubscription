"""
Example usage of Product Research Agent with AI capabilities
Demonstrates hybrid approach: rule-based + AI fallback
"""

from product_research_agent import ProductResearchAgent
import os


def main():
    print("=" * 70)
    print("PRODUCT RESEARCH AGENT - AI-ENHANCED VERSION")
    print("=" * 70)
    print()
    
    # Initialize agent with AI capabilities
    # Option 1: Pass OpenAI API key directly
    # agent = ProductResearchAgent(
    #     api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
    #     search_engine_id="f080b786cd52e44c4",
    #     openai_api_key="your-openai-api-key-here"
    # )
    
    # Option 2: Use environment variable (recommended)
    # Set: export OPENAI_API_KEY="your-key-here"
    agent = ProductResearchAgent(
        api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4",
        use_ai=True  # Enable AI fallback
    )
    
    # Check if AI is available
    if agent.openai_api_key:
        print("✓ AI Enhancement: ENABLED (GPT-4o-mini)")
        print("  - Rule-based extraction runs first (free)")
        print("  - AI fallback for low-quality results (~$0.002-0.005 per call)")
    else:
        print("⚠ AI Enhancement: DISABLED (no OpenAI API key)")
        print("  Set OPENAI_API_KEY environment variable to enable")
    
    print()
    
    # Example 1: Product with good rule-based extraction
    print("=" * 70)
    print("Example 1: High-Quality Rule-Based Extraction")
    print("=" * 70)
    
    result = agent.research("GE", "JGB735SPSS", "range")
    
    if result.success:
        print(f"✓ Success!")
        print(f"  Extraction Method: {result.extraction_method}")
        print(f"  Size: {result.product.size}")
        print(f"  Fuel: {result.product.fuel}")
        print(f"  Features: {len(result.product.features)} detected")
        print(f"  Confidence: {result.confidence}")
        
        if result.extraction_method == "rule-based":
            print("  💰 Cost: ~$0.001 (Google Search only)")
        else:
            print("  💰 Cost: ~$0.005 (Google + AI)")
    
    print()
    
    # Example 2: Force AI extraction
    if agent.openai_api_key:
        print("=" * 70)
        print("Example 2: Forced AI Extraction (for comparison)")
        print("=" * 70)
        
        result_ai = agent.research("GE", "JGB735SPSS", "range", force_ai=True)
        
        if result_ai.success:
            print(f"✓ Success!")
            print(f"  Extraction Method: {result_ai.extraction_method}")
            print(f"  Size: {result_ai.product.size}")
            print(f"  Fuel: {result_ai.product.fuel}")
            print(f"  Features: {len(result_ai.product.features)} detected")
            print(f"  Feature list: {', '.join(result_ai.product.features[:5])}...")
            print(f"  💰 Cost: ~$0.005 (Google + AI)")
        
        print()
    
    # Example 3: Product that might need AI
    print("=" * 70)
    print("Example 3: Hybrid Approach (AI fallback if needed)")
    print("=" * 70)
    
    result = agent.research("Bosch", "SHPM88Z75N", "dishwasher")
    
    if result.success:
        print(f"✓ Success!")
        print(f"  Extraction Method: {result.extraction_method}")
        print(f"  Size: {result.product.size or 'N/A'}")
        print(f"  Features: {len(result.product.features)} detected")
        
        if result.extraction_method == "ai":
            print("  ℹ️  AI was used because rule-based quality was low")
            print("  💰 Cost: ~$0.005")
        else:
            print("  ℹ️  Rule-based extraction was sufficient")
            print("  💰 Cost: ~$0.001")
    
    print()
    
    # Example 4: Disable AI (rule-based only)
    print("=" * 70)
    print("Example 4: Rule-Based Only (AI Disabled)")
    print("=" * 70)
    
    agent_no_ai = ProductResearchAgent(
        api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4",
        use_ai=False  # Disable AI
    )
    
    result = agent_no_ai.research("Samsung", "RF28R7351SR", "refrigerator")
    
    if result.success:
        print(f"✓ Success!")
        print(f"  Extraction Method: {result.extraction_method}")
        print(f"  Size: {result.product.size or 'N/A'}")
        print(f"  Features: {len(result.product.features)} detected")
        print(f"  💰 Cost: ~$0.001 (cheapest option)")
    
    print()
    
    # Cost comparison
    print("=" * 70)
    print("COST COMPARISON (per product)")
    print("=" * 70)
    print()
    print("Rule-Based Only (use_ai=False):")
    print("  Cost: ~$0.001 per product")
    print("  Accuracy: 70-80%")
    print("  Speed: Fast")
    print()
    print("Hybrid Approach (use_ai=True, default):")
    print("  Cost: ~$0.001-0.005 per product (avg ~$0.003)")
    print("  Accuracy: 85-90%")
    print("  Speed: Fast (AI only when needed)")
    print("  Best for: Production use")
    print()
    print("AI Always (force_ai=True):")
    print("  Cost: ~$0.005 per product")
    print("  Accuracy: 90-95%")
    print("  Speed: Slower")
    print("  Best for: Critical accuracy needs")
    print()
    print("=" * 70)
    print()
    
    # Batch processing example
    if agent.openai_api_key:
        print("=" * 70)
        print("Example 5: Batch Processing with Cost Tracking")
        print("=" * 70)
        
        products = [
            {"brand": "GE", "model": "JGB735", "type": "range"},
            {"brand": "Whirlpool", "model": "WFG505M0BS", "type": "range"},
            {"brand": "LG", "model": "LDT7808SS", "type": "dishwasher"},
        ]
        
        total_cost = 0
        ai_count = 0
        rule_count = 0
        
        for product in products:
            result = agent.research(
                brand=product["brand"],
                model=product["model"],
                appliance_type=product["type"]
            )
            
            if result.success:
                if result.extraction_method == "ai":
                    total_cost += 0.005
                    ai_count += 1
                    method_symbol = "🤖"
                else:
                    total_cost += 0.001
                    rule_count += 1
                    method_symbol = "📏"
                
                print(f"{method_symbol} {product['brand']} {product['model']}: {result.extraction_method}")
        
        print()
        print(f"Summary:")
        print(f"  Rule-based: {rule_count} products")
        print(f"  AI-enhanced: {ai_count} products")
        print(f"  Total cost: ~${total_cost:.3f}")
        print(f"  Average: ~${total_cost/len(products):.3f} per product")
        print()


if __name__ == "__main__":
    main()
