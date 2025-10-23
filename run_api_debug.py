"""
Debug version of API server with detailed logging
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from product_research_agent import ProductResearchAgent
from replacement_search_agent import ReplacementSearchAgent
import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize agents
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID', 'f080b786cd52e44c4')

logger.info(f"Initializing agents with API key: {GOOGLE_API_KEY[:20]}...")

research_agent = ProductResearchAgent(
    api_key=GOOGLE_API_KEY,
    search_engine_id=SEARCH_ENGINE_ID,
    use_ai=True
)

replacement_agent = ReplacementSearchAgent(
    google_api_key=GOOGLE_API_KEY,
    search_engine_id=SEARCH_ENGINE_ID
)

logger.info("Agents initialized successfully")


@app.route('/api/health', methods=['GET'])
def health_check():
    logger.info("Health check requested")
    return jsonify({
        'status': 'healthy',
        'service': 'Product Research API',
        'version': '1.0.0'
    })


@app.route('/api/complete', methods=['POST'])
def complete_workflow():
    try:
        data = request.json
        logger.info(f"Complete workflow request received: {data}")
        
        # Validate input
        required = ['brand', 'model', 'appliance_type']
        if not data or not all(k in data for k in required):
            logger.error(f"Missing required fields: {required}")
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(required)}'
            }), 400
        
        brand = data['brand']
        model = data['model']
        appliance_type = data['appliance_type'].lower()
        
        logger.info(f"Step 1: Researching product - {brand} {model} ({appliance_type})")
        
        # Step 1: Research original product
        research_result = research_agent.research(brand, model, appliance_type)
        
        logger.info(f"Research result: success={research_result.success}")
        
        if not research_result.success:
            logger.error(f"Research failed: {research_result.error}")
            return jsonify({
                'success': False,
                'error': research_result.error,
                'stage': 'research'
            }), 400
        
        logger.info(f"Product found: {research_result.product.type}, {research_result.product.size}, {research_result.product.fuel}")
        
        # Step 2: Find replacements
        product_spec = {
            'brand': brand,
            'model': model,
            'type': research_result.product.type,
            'size': research_result.product.size,
            'fuel': research_result.product.fuel,
            'features': research_result.product.features
        }
        
        logger.info(f"Step 2: Finding replacements with spec: {product_spec}")
        
        replacement_result = replacement_agent.search(product_spec)
        
        logger.info(f"Replacement search: found {len(replacement_result.replacements)} products")
        
        # Apply filters
        replacements = replacement_result.replacements
        
        if data.get('brand_for_brand', False):
            logger.info(f"Filtering for brand-for-brand: {brand}")
            replacements = [r for r in replacements if r.brand and r.brand.upper() == brand.upper()]
            logger.info(f"After brand filter: {len(replacements)} products")
        
        if data.get('dollar_limit'):
            dollar_limit = float(data['dollar_limit'])
            logger.info(f"Filtering by dollar limit: ${dollar_limit}")
            replacements = [r for r in replacements if r.price and r.price <= dollar_limit]
            logger.info(f"After price filter: {len(replacements)} products")
        
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
        
        logger.info(f"Sending response with {len(response['replacements'])} replacements")
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Error in complete_workflow: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 70)
    print("Product Research API Server (DEBUG MODE)")
    print("=" * 70)
    print()
    print("Endpoints:")
    print("  GET  /api/health          - Health check")
    print("  POST /api/complete        - Complete workflow")
    print()
    print("Starting server on http://localhost:5001")
    print("Logs will appear below:")
    print("=" * 70)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
