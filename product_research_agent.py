"""
Product Research Agent
Specialized in finding and extracting appliance specifications from web search results.
Hybrid approach: Rule-based extraction with AI fallback for improved accuracy.
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ProductSpecification:
    """Structured product specification data"""
    type: Optional[str] = None
    size: Optional[str] = None
    fuel: Optional[str] = None
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []


@dataclass
class ResearchResult:
    """Research result with metadata"""
    success: bool
    product: Optional[ProductSpecification] = None
    source: Optional[str] = None
    confidence: Optional[str] = None
    error: Optional[str] = None
    extraction_method: Optional[str] = None  # 'rule-based' or 'ai'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {
            "success": self.success
        }
        
        if self.product:
            result["product"] = asdict(self.product)
        else:
            result["product"] = None
            
        if self.source:
            result["source"] = self.source
        if self.confidence:
            result["confidence"] = self.confidence
        if self.error:
            result["error"] = self.error
        if self.extraction_method:
            result["extraction_method"] = self.extraction_method
            
        return result


class ProductResearchAgent:
    """
    Agent specialized in finding and extracting appliance specifications
    from web search results using Google Custom Search API.
    """
    
    # Feature keywords for different appliance types
    RANGE_FEATURES = {
        'convection', 'air fryer', 'air fry', 'self-cleaning', 'self cleaning',
        'double oven', 'burner', 'burners', 'storage drawer', 'griddle',
        'warming drawer', 'precise simmer', 'power boil', 'sealed burners',
        'continuous grates', 'wifi', 'smart', 'steam clean', 'lp convertible',
        'dual fuel', 'induction'
    }
    
    DISHWASHER_FEATURES = {
        'quiet', 'decibel', 'db', 'third rack', 'soil sensor', 'stainless steel tub',
        'energy star', 'bottle jets', 'hard food disposer', 'wifi', 'smart',
        'dry boost', 'sanitize', 'steam', 'adjustable rack', 'cycles'
    }
    
    REFRIGERATOR_FEATURES = {
        'ice maker', 'water dispenser', 'french door', 'side by side',
        'bottom freezer', 'top freezer', 'smart', 'wifi', 'energy star',
        'door in door', 'flex zone', 'dual ice maker', 'craft ice',
        'shelves', 'humidity control', 'led lighting', 'fingerprint resistant'
    }
    
    MICROWAVE_FEATURES = {
        'convection', 'sensor cooking', 'inverter', 'smart', 'wifi',
        'over the range', 'countertop', 'built-in', 'ventilation',
        'turntable', 'power levels', 'auto defrost', 'child lock'
    }
    
    def __init__(self, api_key: str, search_engine_id: str, openai_api_key: Optional[str] = None, use_ai: bool = True):
        """
        Initialize the Product Research Agent
        
        Args:
            api_key: Google Custom Search API key
            search_engine_id: Google Custom Search Engine ID (cx parameter)
            openai_api_key: OpenAI API key (optional, can use env var OPENAI_API_KEY)
            use_ai: Enable AI fallback for better extraction (default: True)
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.api_endpoint = "https://www.googleapis.com/customsearch/v1"
        self.use_ai = use_ai
        
        # OpenAI configuration
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.use_ai and self.openai_api_key:
            self.openai_endpoint = "https://api.openai.com/v1/chat/completions"
            self.openai_model = "gpt-4o-mini"  # Cost-efficient model
        
    def search(self, brand: str, model: str, num_results: int = 10) -> Optional[Dict[str, Any]]:
        """
        Execute Google Custom Search API query
        
        Args:
            brand: Product brand name
            model: Product model number
            num_results: Number of results to retrieve (max 10)
            
        Returns:
            Search results as dictionary or None if error
        """
        query = f"{brand} {model} specifications"
        
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(num_results, 10)
        }
        
        try:
            response = requests.get(self.api_endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Search API error: {e}")
            return None
    
    def _extract_size(self, text: str, appliance_type: str) -> Optional[str]:
        """
        Extract size information from text
        
        Args:
            text: Text to search for size information
            appliance_type: Type of appliance
            
        Returns:
            Size string with units or None
        """
        text_lower = text.lower()
        
        # Common size patterns
        import re
        
        # For ranges, dishwashers, microwaves - look for inch measurements
        if appliance_type in ['range', 'dishwasher', 'microwave']:
            # Match patterns like "30 inch", "30-inch", "30\"", "24 in"
            inch_pattern = r'(\d+)\s*(?:inch|in|")'
            match = re.search(inch_pattern, text_lower)
            if match:
                return f"{match.group(1)} inch"
        
        # For refrigerators - look for cubic feet
        if appliance_type == 'refrigerator':
            # Match patterns like "25 cu ft", "25 cubic feet", "25 cu. ft."
            cuft_pattern = r'(\d+(?:\.\d+)?)\s*(?:cu\.?\s*ft|cubic\s+feet)'
            match = re.search(cuft_pattern, text_lower)
            if match:
                return f"{match.group(1)} cubic feet"
            
            # Also check for inch measurements (width)
            inch_pattern = r'(\d+)\s*(?:inch|in|")'
            match = re.search(inch_pattern, text_lower)
            if match:
                return f"{match.group(1)} inch"
        
        return None
    
    def _extract_fuel_type(self, text: str) -> Optional[str]:
        """
        Extract fuel/power type from text
        
        Args:
            text: Text to search for fuel type
            
        Returns:
            Fuel type string or None
        """
        text_lower = text.lower()
        
        if 'dual fuel' in text_lower:
            return 'dual'
        elif 'gas' in text_lower:
            return 'gas'
        elif 'electric' in text_lower or 'induction' in text_lower:
            return 'electric'
        elif 'propane' in text_lower:
            return 'propane'
        
        return None
    
    def _extract_features(self, text: str, appliance_type: str) -> List[str]:
        """
        Extract features from text based on appliance type
        
        Args:
            text: Text to search for features
            appliance_type: Type of appliance
            
        Returns:
            List of extracted features
        """
        text_lower = text.lower()
        features = []
        
        # Select feature set based on appliance type
        feature_keywords = set()
        if appliance_type == 'range':
            feature_keywords = self.RANGE_FEATURES
        elif appliance_type == 'dishwasher':
            feature_keywords = self.DISHWASHER_FEATURES
        elif appliance_type == 'refrigerator':
            feature_keywords = self.REFRIGERATOR_FEATURES
        elif appliance_type == 'microwave':
            feature_keywords = self.MICROWAVE_FEATURES
        
        # Check for each feature keyword
        for keyword in feature_keywords:
            if keyword in text_lower:
                # Normalize feature name
                feature_name = keyword.replace('-', ' ')
                if feature_name not in features:
                    features.append(feature_name)
        
        # Extract burner count for ranges
        if appliance_type == 'range':
            import re
            burner_match = re.search(r'(\d+)\s*burner', text_lower)
            if burner_match:
                burner_feature = f"{burner_match.group(1)} burners"
                if burner_feature not in features:
                    features.append(burner_feature)
        
        # Extract decibel rating for dishwashers
        if appliance_type == 'dishwasher':
            import re
            db_match = re.search(r'(\d+)\s*(?:db|decibel)', text_lower)
            if db_match:
                db_feature = f"{db_match.group(1)} decibels"
                if db_feature not in features:
                    features.append(db_feature)
        
        return features
    
    def _assess_extraction_quality(self, spec: ProductSpecification) -> float:
        """
        Assess quality of rule-based extraction (0.0 to 1.0)
        
        Args:
            spec: ProductSpecification object
            
        Returns:
            Quality score (0.0 = poor, 1.0 = excellent)
        """
        score = 0.0
        
        # Check if size was extracted
        if spec.size:
            score += 0.3
        
        # Check if fuel type was extracted (for applicable types)
        if spec.fuel and spec.fuel != 'not applicable':
            score += 0.2
        elif spec.fuel == 'not applicable':
            score += 0.2  # Still good for non-fuel appliances
        
        # Check feature count
        if len(spec.features) >= 5:
            score += 0.5
        elif len(spec.features) >= 3:
            score += 0.3
        elif len(spec.features) >= 1:
            score += 0.1
        
        return score
    
    def _extract_with_ai(self, search_results: Dict[str, Any], appliance_type: str) -> Optional[ProductSpecification]:
        """
        Use AI (GPT-4o-mini) to extract specifications from search results
        
        Args:
            search_results: Google Custom Search API results
            appliance_type: Type of appliance
            
        Returns:
            ProductSpecification object or None if AI extraction fails
        """
        if not self.openai_api_key:
            return None
        
        # Prepare search results text
        search_text = ""
        for i, item in enumerate(search_results.get('items', [])[:5], 1):
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            search_text += f"Result {i}:\nTitle: {title}\nSnippet: {snippet}\n\n"
        
        # Create prompt for AI
        prompt = f"""Extract product specifications from these search results for a {appliance_type}.

Search Results:
{search_text}

Extract and return ONLY a JSON object with this exact structure:
{{
  "size": "size with units (e.g., '30 inch', '25 cubic feet') or null",
  "fuel": "gas/electric/dual/propane/not applicable or null",
  "features": ["feature1", "feature2", ...]
}}

Rules:
- For size: Include units (inch for width, cubic feet for capacity)
- For fuel: Only for ranges/ovens (use 'not applicable' for other appliances)
- For features: Extract key features as lowercase strings
- Return null if information is not found
- Return ONLY the JSON object, no other text"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.openai_model,
                "messages": [
                    {"role": "system", "content": "You are a product specification extraction expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            response = requests.post(self.openai_endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content'].strip()
            
            # Parse JSON response
            # Remove markdown code blocks if present
            if ai_response.startswith('```'):
                ai_response = ai_response.split('\n', 1)[1]
                ai_response = ai_response.rsplit('```', 1)[0]
            
            spec_data = json.loads(ai_response)
            
            # Create ProductSpecification from AI response
            spec = ProductSpecification(
                type=appliance_type,
                size=spec_data.get('size'),
                fuel=spec_data.get('fuel'),
                features=spec_data.get('features', [])
            )
            
            return spec
            
        except Exception as e:
            print(f"AI extraction error: {e}")
            return None
    
    def _determine_confidence(self, source_url: str) -> str:
        """
        Determine confidence level based on source
        
        Args:
            source_url: URL of the source
            
        Returns:
            Confidence level: 'high', 'medium', or 'low'
        """
        url_lower = source_url.lower()
        
        # High confidence - manufacturer or official sites
        manufacturer_domains = [
            'geappliances.com', 'whirlpool.com', 'samsung.com', 'lg.com',
            'kitchenaid.com', 'bosch-home.com', 'frigidaire.com', 'electrolux.com',
            'maytag.com', 'thermador.com', 'jenn-air.com', 'ge.com'
        ]
        
        for domain in manufacturer_domains:
            if domain in url_lower:
                return 'high'
        
        # Medium confidence - major retailers
        retailer_domains = [
            'homedepot.com', 'lowes.com', 'bestbuy.com', 'ajmadison.com',
            'appliancesconnection.com', 'abt.com', 'yale.com', 'amazon.com'
        ]
        
        for domain in retailer_domains:
            if domain in url_lower:
                return 'medium'
        
        # Low confidence - other sources
        return 'low'
    
    def analyze_results(self, search_results: Dict[str, Any], appliance_type: str) -> ProductSpecification:
        """
        Analyze search results and extract product specifications
        
        Args:
            search_results: Google Custom Search API results
            appliance_type: Type of appliance
            
        Returns:
            ProductSpecification object
        """
        spec = ProductSpecification(type=appliance_type)
        
        if 'items' not in search_results:
            return spec
        
        all_text = ""
        
        # Collect all text from search results
        for item in search_results['items']:
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            all_text += f" {title} {snippet}"
        
        # Extract size
        spec.size = self._extract_size(all_text, appliance_type)
        
        # Extract fuel type (only relevant for ranges/ovens)
        if appliance_type in ['range', 'oven', 'cooktop']:
            spec.fuel = self._extract_fuel_type(all_text)
        else:
            spec.fuel = 'not applicable'
        
        # Extract features
        spec.features = self._extract_features(all_text, appliance_type)
        
        return spec
    
    def research(self, brand: str, model: str, appliance_type: str, force_ai: bool = False) -> ResearchResult:
        """
        Execute complete research workflow with hybrid extraction
        
        Args:
            brand: Product brand name
            model: Product model number
            appliance_type: Type of appliance
            force_ai: Force AI extraction even if rule-based is good (default: False)
            
        Returns:
            ResearchResult object with findings
        """
        # Step 1: Search
        search_results = self.search(brand, model)
        
        if search_results is None:
            return ResearchResult(
                success=False,
                error="Search API error"
            )
        
        if 'items' not in search_results or len(search_results['items']) == 0:
            return ResearchResult(
                success=False,
                error=f"No search results found for {brand} {model}"
            )
        
        # Step 2: Try rule-based extraction first
        product_spec = self.analyze_results(search_results, appliance_type)
        extraction_method = "rule-based"
        
        # Step 3: Assess quality and use AI if needed
        quality_score = self._assess_extraction_quality(product_spec)
        
        if self.use_ai and (quality_score < 0.7 or force_ai):
            # Quality is low, try AI extraction
            ai_spec = self._extract_with_ai(search_results, appliance_type)
            
            if ai_spec:
                # Use AI result if it's better
                ai_quality = self._assess_extraction_quality(ai_spec)
                
                if ai_quality > quality_score or force_ai:
                    product_spec = ai_spec
                    extraction_method = "ai"
        
        # Step 4: Determine source and confidence
        primary_source = search_results['items'][0]['link']
        confidence = self._determine_confidence(primary_source)
        
        # Extract domain for source description
        from urllib.parse import urlparse
        domain = urlparse(primary_source).netloc
        
        return ResearchResult(
            success=True,
            product=product_spec,
            source=domain,
            confidence=confidence,
            extraction_method=extraction_method
        )
    
    def research_json(self, brand: str, model: str, appliance_type: str) -> str:
        """
        Execute research and return JSON string
        
        Args:
            brand: Product brand name
            model: Product model number
            appliance_type: Type of appliance
            
        Returns:
            JSON string with research results
        """
        result = self.research(brand, model, appliance_type)
        return json.dumps(result.to_dict(), indent=2)


# Example usage
if __name__ == "__main__":
    # Initialize agent
    API_KEY = "AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E"
    SEARCH_ENGINE_ID = "f080b786cd52e44c4"
    
    agent = ProductResearchAgent(API_KEY, SEARCH_ENGINE_ID)
    
    # Research a product
    result_json = agent.research_json(
        brand="GE",
        model="JGB735",
        appliance_type="range"
    )
    
    print(result_json)
