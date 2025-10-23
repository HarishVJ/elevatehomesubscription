"""
Example: Using Product Research Agent + Replacement Search Agent together
"""

from product_research_agent import ProductResearchAgent
from replacement_search_agent import ReplacementSearchAgent


def main():
    print("=" * 70)
    print("COMPLETE WORKFLOW: Research + Find Replacements")
    print("=" * 70)
    print()
    
    # Initialize both agents
    research_agent = ProductResearchAgent(
        api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4",
        use_ai=False  # Use rule-based for speed
    )
    
    replacement_agent = ReplacementSearchAgent(
        google_api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4"
    )
    
    # Example 1: Research original product
    print("STEP 1: Research Original Product")
    print("-" * 70)
    
    brand = "GE"
    model = "JGB735"
    appliance_type = "range"
    
    print(f"Researching: {brand} {model} ({appliance_type})")
    
    original = research_agent.research(brand, model, appliance_type)
    
    if not original.success:
        print(f"✗ Error: {original.error}")
        return
    
    print(f"✓ Found original product:")
    print(f"  Type: {original.product.type}")
    print(f"  Size: {original.product.size}")
    print(f"  Fuel: {original.product.fuel}")
    print(f"  Features: {', '.join(original.product.features[:5])}")
    print(f"  Source: {original.source}")
    print()
    
    # Example 2: Find replacements
    print("STEP 2: Find Replacement Products")
    print("-" * 70)
    
    # Convert to product spec format
    product_spec = {
        "brand": brand,
        "model": model,
        "type": original.product.type,
        "size": original.product.size,
        "fuel": original.product.fuel,
        "features": original.product.features
    }
    
    print(f"Searching across retailers...")
    
    replacements = replacement_agent.search(product_spec)
    
    if not replacements.success:
        print(f"✗ Error: {replacements.error}")
        return
    
    print(f"✓ Search complete:")
    print(f"  Retailers searched: {replacements.search_summary['retailers_searched']}")
    print(f"  Total products found: {replacements.search_summary['total_products_found']}")
    print(f"  Viable matches: {replacements.search_summary['viable_matches']}")
    print()
    
    # Example 3: Display top matches
    if len(replacements.replacements) == 0:
        print("No replacement products found.")
        if replacements.message:
            print(f"Message: {replacements.message}")
        return
    
    print("STEP 3: Top Replacement Options")
    print("-" * 70)
    
    for match in replacements.replacements[:5]:  # Show top 5
        print(f"\n{match.rank}. {match.product_name}")
        print(f"   Brand: {match.brand or 'Unknown'}")
        print(f"   Model: {match.model or 'N/A'}")
        print(f"   Price: ${match.price:.2f}" if match.price else "   Price: Not available")
        print(f"   Size: {match.size or 'N/A'}")
        print(f"   Fuel: {match.fuel or 'N/A'}")
        print(f"   Retailer: {match.retailer}")
        print(f"   Availability: {match.availability}")
        print(f"   Match Score: {match.match_score}/100")
        
        # Show match details
        details = match.match_details
        if details['features_matched']:
            print(f"   ✓ Matched features: {', '.join(details['features_matched'][:3])}")
        if details['features_missing']:
            print(f"   ✗ Missing features: {', '.join(details['features_missing'][:3])}")
        
        print(f"   URL: {match.url[:60]}...")
    
    print()
    print("=" * 70)
    
    # Example 4: Filter results
    print("\nFILTERED RESULTS")
    print("-" * 70)
    
    # In stock only
    in_stock = [m for m in replacements.replacements if m.availability == 'in stock']
    print(f"\nIn Stock: {len(in_stock)} products")
    for match in in_stock[:3]:
        print(f"  • {match.product_name} - ${match.price if match.price else 'N/A'}")
    
    # With prices
    with_prices = [m for m in replacements.replacements if m.price]
    if with_prices:
        print(f"\nWith Prices: {len(with_prices)} products")
        cheapest = min(with_prices, key=lambda m: m.price)
        print(f"  Cheapest: {cheapest.product_name} - ${cheapest.price:.2f}")
        
        most_expensive = max(with_prices, key=lambda m: m.price)
        print(f"  Most expensive: {most_expensive.product_name} - ${most_expensive.price:.2f}")
    
    # By retailer
    print(f"\nBy Retailer:")
    retailers = {}
    for match in replacements.replacements:
        retailers[match.retailer] = retailers.get(match.retailer, 0) + 1
    
    for retailer, count in sorted(retailers.items(), key=lambda x: -x[1]):
        print(f"  {retailer}: {count} products")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
