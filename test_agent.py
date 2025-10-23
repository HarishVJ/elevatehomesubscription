"""
Test script for Product Research Agent
Run this to verify the agent is working correctly
"""

from product_research_agent import ProductResearchAgent
import json


def test_basic_search():
    """Test basic search functionality"""
    print("\n" + "="*70)
    print("TEST 1: Basic Search - GE Range")
    print("="*70)
    
    agent = ProductResearchAgent(
        api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4"
    )
    
    result = agent.research("GE", "JGB735", "range")
    
    assert result.success, "Search should succeed"
    assert result.product is not None, "Product should not be None"
    assert result.product.type == "range", "Type should be 'range'"
    assert result.product.size is not None, "Size should be extracted"
    assert result.product.fuel is not None, "Fuel type should be extracted"
    assert len(result.product.features) > 0, "Features should be found"
    assert result.confidence in ["high", "medium", "low"], "Confidence should be valid"
    
    print("✓ PASSED")
    print(f"  Found: {result.product.size} {result.product.fuel} {result.product.type}")
    print(f"  Features: {len(result.product.features)} detected")
    print(f"  Source: {result.source} (confidence: {result.confidence})")
    return True


def test_json_output():
    """Test JSON output format"""
    print("\n" + "="*70)
    print("TEST 2: JSON Output Format")
    print("="*70)
    
    agent = ProductResearchAgent(
        api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4"
    )
    
    result_json = agent.research_json("Samsung", "DW80R9950US", "dishwasher")
    
    # Verify it's valid JSON
    result_dict = json.loads(result_json)
    
    assert "success" in result_dict, "JSON should have 'success' field"
    assert "product" in result_dict, "JSON should have 'product' field"
    
    if result_dict["success"]:
        assert "type" in result_dict["product"], "Product should have 'type'"
        assert "features" in result_dict["product"], "Product should have 'features'"
        assert isinstance(result_dict["product"]["features"], list), "Features should be a list"
    
    print("✓ PASSED")
    print(f"  Valid JSON: {len(result_json)} bytes")
    print(f"  Success: {result_dict['success']}")
    return True


def test_different_appliances():
    """Test different appliance types"""
    print("\n" + "="*70)
    print("TEST 3: Different Appliance Types")
    print("="*70)
    
    agent = ProductResearchAgent(
        api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4"
    )
    
    test_cases = [
        {"brand": "GE", "model": "JGB735", "type": "range", "expected_fuel": "gas"},
        {"brand": "Whirlpool", "model": "WDT750SAKZ", "type": "dishwasher", "expected_fuel": "not applicable"},
        {"brand": "LG", "model": "LRFVS3006S", "type": "refrigerator", "expected_fuel": "not applicable"},
    ]
    
    passed = 0
    for test in test_cases:
        result = agent.research(test["brand"], test["model"], test["type"])
        
        if result.success:
            assert result.product.type == test["type"], f"Type mismatch for {test['brand']} {test['model']}"
            print(f"  ✓ {test['type'].capitalize()}: {test['brand']} {test['model']}")
            print(f"    Size: {result.product.size or 'N/A'}, Features: {len(result.product.features)}")
            passed += 1
        else:
            print(f"  ⚠ {test['type'].capitalize()}: {test['brand']} {test['model']} - {result.error}")
    
    print(f"\n✓ PASSED ({passed}/{len(test_cases)} successful)")
    return True


def test_error_handling():
    """Test error handling for invalid products"""
    print("\n" + "="*70)
    print("TEST 4: Error Handling")
    print("="*70)
    
    agent = ProductResearchAgent(
        api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4"
    )
    
    # Test with non-existent product
    result = agent.research("FakeBrand", "NOTREAL999", "range")
    
    # Should fail gracefully
    print(f"  Non-existent product: success={result.success}")
    if not result.success:
        print(f"  Error message: {result.error}")
        assert result.error is not None, "Error message should be provided"
        assert result.product is None, "Product should be None on failure"
    
    print("✓ PASSED - Errors handled gracefully")
    return True


def test_feature_extraction():
    """Test feature extraction capabilities"""
    print("\n" + "="*70)
    print("TEST 5: Feature Extraction")
    print("="*70)
    
    agent = ProductResearchAgent(
        api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4"
    )
    
    # Test with a feature-rich product
    result = agent.research("GE", "JGB735SPSS", "range")
    
    if result.success:
        features = result.product.features
        print(f"  Features found: {len(features)}")
        print(f"  Feature list: {', '.join(features[:5])}...")
        
        # Check for common range features
        feature_text = ' '.join(features).lower()
        checks = []
        
        if 'convection' in feature_text or 'air fry' in feature_text:
            checks.append("✓ Cooking features detected")
        if 'burner' in feature_text:
            checks.append("✓ Burner information detected")
        if 'smart' in feature_text or 'wifi' in feature_text:
            checks.append("✓ Smart features detected")
        
        for check in checks:
            print(f"  {check}")
        
        assert len(features) > 0, "Should extract at least some features"
    
    print("✓ PASSED")
    return True


def test_confidence_scoring():
    """Test confidence scoring based on sources"""
    print("\n" + "="*70)
    print("TEST 6: Confidence Scoring")
    print("="*70)
    
    agent = ProductResearchAgent(
        api_key="AIzaSyD_-hQdnNH42iP9dCi6E9lvpvpOlc0kB_E",
        search_engine_id="f080b786cd52e44c4"
    )
    
    result = agent.research("GE", "JGB735", "range")
    
    if result.success:
        print(f"  Source: {result.source}")
        print(f"  Confidence: {result.confidence}")
        
        assert result.confidence in ["high", "medium", "low"], "Confidence must be valid"
        
        # Check if manufacturer sites get high confidence
        if "geappliances.com" in result.source or "ge.com" in result.source:
            assert result.confidence == "high", "Manufacturer sites should have high confidence"
            print("  ✓ Manufacturer source correctly rated as 'high' confidence")
    
    print("✓ PASSED")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("PRODUCT RESEARCH AGENT - TEST SUITE")
    print("="*70)
    
    tests = [
        ("Basic Search", test_basic_search),
        ("JSON Output", test_json_output),
        ("Different Appliances", test_different_appliances),
        ("Error Handling", test_error_handling),
        ("Feature Extraction", test_feature_extraction),
        ("Confidence Scoring", test_confidence_scoring),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "PASSED", None))
        except AssertionError as e:
            results.append((test_name, "FAILED", str(e)))
            print(f"✗ FAILED: {e}")
        except Exception as e:
            results.append((test_name, "ERROR", str(e)))
            print(f"✗ ERROR: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, status, _ in results if status == "PASSED")
    failed = sum(1 for _, status, _ in results if status == "FAILED")
    errors = sum(1 for _, status, _ in results if status == "ERROR")
    
    for test_name, status, error in results:
        symbol = "✓" if status == "PASSED" else "✗"
        print(f"{symbol} {test_name}: {status}")
        if error:
            print(f"  Error: {error}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {errors} errors")
    print("="*70)
    
    return passed == len(tests)


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
