"""
Replacement Search Agent
Finds comparable appliance replacements from multiple retail websites.
"""

import requests
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ProductMatch:
    """Matched replacement product"""
    rank: int
    product_name: str
    brand: Optional[str]
    model: Optional[str]
    price: Optional[float]
    size: Optional[str]
    fuel: Optional[str]
    features: List[str]
    url: str
    retailer: str
    availability: str
    match_score: int
    match_details: Dict[str, Any]


@dataclass
class SearchResult:
    """Search result with summary"""
    success: bool
    search_summary: Dict[str, int]
    original_product: Dict[str, Any]
    replacements: List[ProductMatch]
    message: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "success": self.success,
            "search_summary": self.search_summary,
            "original_product": self.original_product,
            "replacements": [asdict(r) for r in self.replacements]
        }
        if self.message:
            result["message"] = self.message
        if self.error:
            result["error"] = self.error
        return result


class ReplacementSearchAgent:
    """
    Agent specialized in finding comparable appliance replacements
    from multiple retail websites.
    """
    
    # Retailers to search
    RETAILERS = {
        "Home Depot": "homedepot.com",
        "Lowe's": "lowes.com",
        "Best Buy": "bestbuy.com",
        "P.C. Richard & Son": "pcrichard.com"
    }
    
    # Scoring constants
    BASE_SCORE = 100
    MIN_VIABLE_SCORE = 60
    SIZE_TOLERANCE = 2  # inches
    
    def __init__(self, google_api_key: str, search_engine_id: str):
        """
        Initialize the Replacement Search Agent
        
        Args:
            google_api_key: Google Custom Search API key
            search_engine_id: Google Custom Search Engine ID
        """
        self.google_api_key = google_api_key
        self.search_engine_id = search_engine_id
        self.api_endpoint = "https://www.googleapis.com/customsearch/v1"
    
    def _construct_query(self, retailer_domain: str, product_spec: Dict[str, Any]) -> str:
        """Construct search query for a retailer"""
        query_parts = [f"site:{retailer_domain}"]
        
        # Add type
        if product_spec.get('type'):
            query_parts.append(product_spec['type'])
        
        # Add size
        if product_spec.get('size'):
            query_parts.append(product_spec['size'])
        
        # Add fuel
        if product_spec.get('fuel') and product_spec['fuel'] != 'not applicable':
            query_parts.append(product_spec['fuel'])
        
        # Add top 2 features
        features = product_spec.get('features', [])
        for feature in features[:2]:
            query_parts.append(feature)
        
        return ' '.join(query_parts)
    
    def _search_retailer(self, retailer_name: str, retailer_domain: str, 
                        product_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search a single retailer"""
        query = self._construct_query(retailer_domain, product_spec)
        
        params = {
            'key': self.google_api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': 10
        }
        
        try:
            response = requests.get(self.api_endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'retailer': retailer_name
                })
            
            return results
        except Exception as e:
            print(f"Search error for {retailer_name}: {e}")
            return []
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        # Look for price patterns: $1,299.99, $1299, 1299.99
        patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_brand(self, text: str) -> Optional[str]:
        """Extract brand from text"""
        brands = [
            'GE', 'Whirlpool', 'LG', 'Samsung', 'Frigidaire', 'KitchenAid',
            'Kenmore', 'Bosch', 'Maytag', 'Electrolux', 'Amana', 'Haier',
            'Thermador', 'Jenn-Air', 'Café', 'Profile', 'Monogram'
        ]
        
        text_upper = text.upper()
        for brand in brands:
            if brand.upper() in text_upper:
                return brand
        
        return None
    
    def _extract_model(self, text: str) -> Optional[str]:
        """Extract model number from text"""
        # Look for alphanumeric model patterns
        pattern = r'\b([A-Z]{2,}[0-9]{3,}[A-Z0-9]*)\b'
        match = re.search(pattern, text)
        return match.group(1) if match else None
    
    def _extract_size(self, text: str, appliance_type: str) -> Optional[str]:
        """Extract size from text"""
        if appliance_type in ['range', 'dishwasher', 'microwave']:
            match = re.search(r'(\d+)\s*(?:inch|in|")', text.lower())
            if match:
                return f"{match.group(1)} inch"
        
        if appliance_type == 'refrigerator':
            match = re.search(r'(\d+(?:\.\d+)?)\s*(?:cu\.?\s*ft|cubic\s+feet)', text.lower())
            if match:
                return f"{match.group(1)} cubic feet"
            
            match = re.search(r'(\d+)\s*(?:inch|in|")', text.lower())
            if match:
                return f"{match.group(1)} inch"
        
        return None
    
    def _extract_fuel(self, text: str) -> Optional[str]:
        """Extract fuel type from text"""
        text_lower = text.lower()
        
        if 'dual fuel' in text_lower:
            return 'dual'
        elif 'gas' in text_lower:
            return 'gas'
        elif 'electric' in text_lower or 'induction' in text_lower:
            return 'electric'
        
        return None
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract features from text"""
        text_lower = text.lower()
        features = []
        
        feature_keywords = [
            'convection', 'air fry', 'air fryer', 'self-cleaning', 'self cleaning',
            'wifi', 'smart', 'double oven', 'storage drawer', 'warming drawer',
            'stainless steel', 'energy star', 'quiet', 'third rack', 'ice maker',
            'water dispenser', 'french door', 'side by side', 'sensor cooking'
        ]
        
        for keyword in feature_keywords:
            if keyword in text_lower:
                features.append(keyword.replace('-', ' '))
        
        # Extract burner count
        burner_match = re.search(r'(\d+)\s*burner', text_lower)
        if burner_match:
            features.append(f"{burner_match.group(1)} burners")
        
        return list(set(features))  # Remove duplicates
    
    def _extract_availability(self, text: str) -> str:
        """Extract availability status"""
        text_lower = text.lower()
        
        if 'in stock' in text_lower or 'available' in text_lower:
            return 'in stock'
        elif 'limited' in text_lower or 'few left' in text_lower:
            return 'limited stock'
        elif 'out of stock' in text_lower or 'unavailable' in text_lower:
            return 'out of stock'
        
        return 'unknown'
    
    def _extract_product_data(self, search_result: Dict[str, Any], 
                             appliance_type: str) -> Dict[str, Any]:
        """Extract structured product data from search result"""
        title = search_result['title']
        snippet = search_result['snippet']
        combined_text = f"{title} {snippet}"
        
        return {
            'product_name': title,
            'brand': self._extract_brand(combined_text),
            'model': self._extract_model(combined_text),
            'price': self._extract_price(combined_text),
            'size': self._extract_size(combined_text, appliance_type),
            'fuel': self._extract_fuel(combined_text),
            'features': self._extract_features(combined_text),
            'url': search_result['url'],
            'retailer': search_result['retailer'],
            'availability': self._extract_availability(combined_text)
        }
    
    def _calculate_match_score(self, product: Dict[str, Any], 
                               original: Dict[str, Any]) -> tuple:
        """Calculate match score and details"""
        score = self.BASE_SCORE
        details = {
            'size_match': False,
            'fuel_match': False,
            'features_matched': [],
            'features_missing': [],
            'price_competitive': product.get('price') is not None
        }
        
        # Critical: Type match (must match)
        if product.get('type') != original.get('type'):
            return 0, details  # Disqualify
        score += 10
        
        # Critical: Size match
        orig_size = original.get('size', '')
        prod_size = product.get('size', '')
        
        if orig_size and prod_size:
            orig_num = int(re.search(r'\d+', orig_size).group()) if re.search(r'\d+', orig_size) else 0
            prod_num = int(re.search(r'\d+', prod_size).group()) if re.search(r'\d+', prod_size) else 0
            
            diff = abs(orig_num - prod_num)
            if diff == 0:
                score += 20
                details['size_match'] = True
            elif diff <= 1:
                score += 15
                details['size_match'] = True
            elif diff <= self.SIZE_TOLERANCE:
                score += 10
                details['size_match'] = True
            else:
                score -= 50  # Outside tolerance
        
        # Critical: Fuel match
        if original.get('fuel') and original['fuel'] != 'not applicable':
            if product.get('fuel') == original['fuel']:
                score += 20
                details['fuel_match'] = True
            else:
                score -= 50  # Wrong fuel type
        else:
            details['fuel_match'] = True  # N/A for this appliance
        
        # Feature matching
        orig_features = set(f.lower() for f in original.get('features', []))
        prod_features = set(f.lower() for f in product.get('features', []))
        
        matched = orig_features & prod_features
        missing = orig_features - prod_features
        
        details['features_matched'] = list(matched)
        details['features_missing'] = list(missing)
        
        # Score features
        score += len(matched) * 10
        score -= len(missing) * 15
        
        # Availability bonus
        availability = product.get('availability', 'unknown')
        if availability == 'in stock':
            score += 10
        elif availability == 'limited stock':
            score += 5
        elif availability == 'unknown':
            score += 3
        
        # Price bonus
        if product.get('price'):
            score += 5
        
        return score, details
    
    def search(self, product_spec: Dict[str, Any]) -> SearchResult:
        """
        Search for replacement products across retailers
        
        Args:
            product_spec: Original product specifications from ProductResearchAgent
            
        Returns:
            SearchResult with ranked replacement options
        """
        all_results = []
        retailers_searched = 0
        
        # Search each retailer
        for retailer_name, retailer_domain in self.RETAILERS.items():
            search_results = self._search_retailer(retailer_name, retailer_domain, product_spec)
            
            if search_results:
                retailers_searched += 1
                
                # Extract product data from each result
                for result in search_results:
                    product_data = self._extract_product_data(result, product_spec['type'])
                    product_data['type'] = product_spec['type']  # Ensure type is set
                    
                    # Calculate match score
                    score, details = self._calculate_match_score(product_data, product_spec)
                    
                    # Only include viable matches
                    if score >= self.MIN_VIABLE_SCORE:
                        all_results.append({
                            'product': product_data,
                            'score': score,
                            'details': details
                        })
        
        # Sort by score (desc), then price (asc)
        all_results.sort(key=lambda x: (
            -x['score'],
            x['product'].get('price') if x['product'].get('price') else float('inf')
        ))
        
        # Take top 10
        top_results = all_results[:10]
        
        # Create ProductMatch objects
        replacements = []
        for rank, result in enumerate(top_results, 1):
            prod = result['product']
            replacements.append(ProductMatch(
                rank=rank,
                product_name=prod['product_name'],
                brand=prod['brand'],
                model=prod['model'],
                price=prod['price'],
                size=prod['size'],
                fuel=prod['fuel'],
                features=prod['features'],
                url=prod['url'],
                retailer=prod['retailer'],
                availability=prod['availability'],
                match_score=result['score'],
                match_details=result['details']
            ))
        
        # Create summary
        search_summary = {
            'retailers_searched': retailers_searched,
            'total_products_found': len(all_results),
            'viable_matches': len(replacements)
        }
        
        # Determine message
        message = None
        if len(replacements) == 0 and len(all_results) > 0:
            message = "Products found but none meet minimum match criteria. Original specifications may be too specific."
        elif len(replacements) == 0:
            message = "No matching products found across searched retailers. Consider broadening search criteria."
        
        return SearchResult(
            success=True,
            search_summary=search_summary,
            original_product=product_spec,
            replacements=replacements,
            message=message
        )
    
    def search_json(self, product_spec: Dict[str, Any]) -> str:
        """
        Search and return JSON string
        
        Args:
            product_spec: Original product specifications
            
        Returns:
            JSON string with results
        """
        result = self.search(product_spec)
        return json.dumps(result.to_dict(), indent=2)


# Example usage
if __name__ == "__main__":
    # Example: Search for replacements for a GE range
    agent = ReplacementSearchAgent(
        google_api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4"
    )
    
    # Original product spec (from ProductResearchAgent)
    original_product = {
        "brand": "GE",
        "model": "JGB735",
        "type": "range",
        "size": "30 inch",
        "fuel": "gas",
        "features": ["convection", "air fry", "self cleaning", "5 burners"]
    }
    
    # Search for replacements
    result_json = agent.search_json(original_product)
    print(result_json)
