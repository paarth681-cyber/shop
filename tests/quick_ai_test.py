#!/usr/bin/env python3
"""
Quick test of AI functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_search():
    """Test AI search functionality"""
    print("🔍 Testing AI Search...")
    
    from ai_engine import get_ai_engine
    
    ai = get_ai_engine()
    ai.initialize()
    
    # Test searches
    test_queries = [
        "gaming laptop",
        "wireless mouse", 
        "4K monitor",
        "bluetooth speaker",
        "mechanical keyboard"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        results = ai.smart_search(query, use_nlp=True, limit=3)
        
        for i, result in enumerate(results, 1):
            relevance = result.get('relevance_score', 0)
            name = result.get('name', 'N/A')
            price = result.get('price', 0)
            print(f"  {i}. {name} - ${price:.2f} (relevance: {relevance:.3f})")

def test_ml_forecast():
    """Test ML forecasting"""
    print("\n📊 Testing ML Forecasting...")
    
    from ai_engine import get_ai_engine
    
    ai = get_ai_engine()
    ai.initialize()
    
    forecast = ai.ml_forecaster.forecast_sales(7)
    
    if "error" not in forecast:
        summary = forecast['summary']
        print(f"7-day forecast: ${summary['total_predicted_sales']:,.2f}")
        print(f"Confidence: {summary['confidence']:.1%}")
        print(f"Trend: {summary['trend']}")
        print(f"Daily average: ${summary['avg_daily_prediction']:,.2f}")
        
        print("\nDaily predictions:")
        for pred in forecast['forecasts'][:5]:  # Show first 5 days
            print(f"  {pred['date']}: ${pred['predicted_sales']:,.2f}")
    else:
        print(f"Error: {forecast['error']}")

def test_capabilities():
    """Test AI capabilities"""
    print("\n🤖 Testing AI Capabilities...")
    
    from ai_engine import get_ai_engine
    
    ai = get_ai_engine()
    ai.initialize()
    
    caps = ai.get_capabilities()
    print(f"Status: {caps['status']}")
    
    for feature, info in caps.items():
        if isinstance(info, dict):
            status = "✅" if info['available'] else "❌"
            print(f"  {status} {feature.replace('_', ' ').title()}: {info['description']}")

if __name__ == "__main__":
    print("🚀 Shop Manager Pro - Quick AI Test")
    print("=" * 50)
    
    test_capabilities()
    test_ai_search()
    test_ml_forecast()
    
    print("\n✅ AI functionality test completed!")