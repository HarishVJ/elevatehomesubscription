// Product Models

export interface ProductSpecification {
  type: string;
  size: string | null;
  fuel: string | null;
  features: string[];
}

export interface OriginalProduct {
  brand: string;
  model: string;
  type: string;
  size: string | null;
  fuel: string | null;
  features: string[];
  source?: string;
  confidence?: string;
  extraction_method?: string;
}

export interface MatchDetails {
  size_match: boolean;
  fuel_match: boolean;
  features_matched: string[];
  features_missing: string[];
  price_competitive: boolean;
}

export interface ReplacementProduct {
  rank: number;
  product_name: string;
  brand: string | null;
  model: string | null;
  price: number | null;
  size: string | null;
  fuel: string | null;
  features: string[];
  url: string;
  retailer: string;
  availability: string;
  match_score: number;
  match_details: MatchDetails;
}

export interface SearchSummary {
  retailers_searched: number;
  total_products_found: number;
  viable_matches: number;
}

export interface SearchRequest {
  brand: string;
  model: string;
  appliance_type: string;
  brand_for_brand: boolean;
  dollar_limit: number | null;
}

export interface SearchResponse {
  success: boolean;
  original_product: OriginalProduct;
  search_summary: SearchSummary;
  replacements: ReplacementProduct[];
  message?: string;
  error?: string;
}

export interface ChatMessage {
  content: string;
  isUser: boolean;
  timestamp: Date;
}
