"""
Simple Flask API server for Product Research Agent
Provides REST endpoints for the Angular web chat interface
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from product_research_agent import ProductResearchAgent
from replacement_search_agent import ReplacementSearchAgent
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for Angular frontend

# Initialize agents
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID', 'f080b786cd52e44c4')

research_agent = ProductResearchAgent(
    api_key=GOOGLE_API_KEY,
    search_engine_id=SEARCH_ENGINE_ID,
    use_ai=True
)

replacement_agent = ReplacementSearchAgent(
    google_api_key=GOOGLE_API_KEY,
    search_engine_id=SEARCH_ENGINE_ID
)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Product Research API',
        'version': '1.0.0'
    })


@app.route('/api/research', methods=['POST'])
def research_product():
    """
    Research a product
    
    Request body:
    {
        "brand": "GE",
        "model": "JGB735",
        "appliance_type": "range"
    }
    """
    try:
        data = request.json
        
        # Validate input
        if not data or not all(k in data for k in ['brand', 'model', 'appliance_type']):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: brand, model, appliance_type'
            }), 400
        
        brand = data['brand']
        model = data['model']
        appliance_type = data['appliance_type'].lower()
        
        # Research product
        result = research_agent.research(brand, model, appliance_type)
        
        # Convert to dict
        response = {
            'success': result.success,
            'product': {
                'type': result.product.type,
                'size': result.product.size,
                'fuel': result.product.fuel,
                'features': result.product.features
            } if result.success else None,
            'source': result.source if result.success else None,
            'confidence': result.confidence if result.success else None,
            'extraction_method': result.extraction_method if result.success else None,
            'error': result.error if not result.success else None
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/replacements', methods=['POST'])
def find_replacements():
    """
    Find replacement products
    
    Request body:
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
    """
    try:
        data = request.json
        
        # Validate input
        required = ['brand', 'model', 'type', 'size', 'fuel', 'features']
        if not data or not all(k in data for k in required):
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(required)}'
            }), 400
        
        # Create product spec
        product_spec = {
            'brand': data['brand'],
            'model': data['model'],
            'type': data['type'],
            'size': data['size'],
            'fuel': data['fuel'],
            'features': data['features']
        }
        
        # Search for replacements
        result = replacement_agent.search(product_spec)
        
        # Apply filters
        replacements = result.replacements
        
        # Filter by brand if brand-for-brand
        if data.get('brand_for_brand', False):
            replacements = [r for r in replacements if r.brand and r.brand.upper() == data['brand'].upper()]
        
        # Filter by dollar limit
        if data.get('dollar_limit'):
            dollar_limit = float(data['dollar_limit'])
            replacements = [r for r in replacements if r.price and r.price <= dollar_limit]
        
        # Convert to dict
        response = {
            'success': result.success,
            'search_summary': result.search_summary,
            'original_product': result.original_product,
            'replacements': [
                {
                    'rank': r.rank,
                    'product_name': r.product_name,
                    'brand': r.brand,
                    'model': r.model,
                    'price': r.price,
                    'size': r.size,
                    'fuel': r.fuel,
                    'features': r.features,
                    'url': r.url,
                    'retailer': r.retailer,
                    'availability': r.availability,
                    'match_score': r.match_score,
                    'match_details': r.match_details
                }
                for r in replacements[:10]  # Top 10
            ],
            'message': result.message,
            'error': result.error
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/complete', methods=['POST'])
def complete_workflow():
    """
    Complete workflow: Research + Find Replacements
    
    Request body:
    {
        "brand": "GE",
        "model": "JGB735",
        "appliance_type": "range",
        "brand_for_brand": false,
        "dollar_limit": 2000
    }
    """
    try:
        data = request.json
        
        # Validate input
        required = ['brand', 'model', 'appliance_type']
        if not data or not all(k in data for k in required):
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(required)}'
            }), 400
        
        brand = data['brand']
        model = data['model']
        appliance_type = data['appliance_type'].lower()
        
        # Step 1: Research original product
        research_result = research_agent.research(brand, model, appliance_type)
        
        if not research_result.success:
            return jsonify({
                'success': False,
                'error': research_result.error,
                'stage': 'research'
            }), 400
        
        # Step 2: Find replacements
        product_spec = {
            'brand': brand,
            'model': model,
            'type': research_result.product.type,
            'size': research_result.product.size,
            'fuel': research_result.product.fuel,
            'features': research_result.product.features
        }
        
        replacement_result = replacement_agent.search(product_spec)
        
        # Apply filters
        replacements = replacement_result.replacements
        
        if data.get('brand_for_brand', False):
            replacements = [r for r in replacements if r.brand and r.brand.upper() == brand.upper()]
        
        if data.get('dollar_limit'):
            dollar_limit = float(data['dollar_limit'])
            replacements = [r for r in replacements if r.price and r.price <= dollar_limit]
        
        # Build response
        response = {
            'success': True,
            'original_product': {
                'brand': brand,
                'model': model,
                'type': research_result.product.type,
                'size': research_result.product.size,
                'fuel': research_result.product.fuel,
                'features': research_result.product.features,
                'source': research_result.source,
                'confidence': research_result.confidence,
                'extraction_method': research_result.extraction_method
            },
            'search_summary': replacement_result.search_summary,
            'replacements': [
                {
                    'rank': i + 1,
                    'product_name': r.product_name,
                    'brand': r.brand,
                    'model': r.model,
                    'price': r.price,
                    'size': r.size,
                    'fuel': r.fuel,
                    'features': r.features,
                    'url': r.url,
                    'retailer': r.retailer,
                    'availability': r.availability,
                    'match_score': r.match_score,
                    'match_details': r.match_details
                }
                for i, r in enumerate(replacements[:10])
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    import os
    
    # Get port from environment variable (for Azure Container Apps)
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("=" * 70)
    print("Product Research API Server")
    print("=" * 70)
    print()
    print("Endpoints:")
    print("  GET  /api/health          - Health check")
    print("  POST /api/research        - Research a product")
    print("  POST /api/replacements    - Find replacements")
    print("  POST /api/complete        - Complete workflow")
    print()
    print(f"Starting server on http://0.0.0.0:{port}")
    print(f"Debug mode: {debug}")
    print("=" * 70)
    print()
    
    app.run(debug=debug, host='0.0.0.0', port=port)
