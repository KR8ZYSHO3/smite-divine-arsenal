#!/usr/bin/env python3
"""
Test script for Divine Arsenal deployment
Run this once your app is live on Render
"""

import requests
import json
import time

def test_deployment(base_url):
    """Test the deployed Divine Arsenal API endpoints"""
    print(f"🧪 Testing Divine Arsenal deployment at: {base_url}")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test key endpoints
    endpoints = [
        "/api/gods",
        "/api/items", 
        "/api/build-optimizer",
        "/api/community/builds",
        "/api/stats"
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if endpoint == "/api/gods":
                    count = len(data) if isinstance(data, list) else data.get('count', 0)
                    print(f"✅ {endpoint}: {count} gods loaded")
                elif endpoint == "/api/items":
                    count = len(data) if isinstance(data, list) else data.get('count', 0)
                    print(f"✅ {endpoint}: {count} items loaded")
                else:
                    print(f"✅ {endpoint}: OK")
                results[endpoint] = "✅ PASS"
            else:
                print(f"❌ {endpoint}: {response.status_code}")
                results[endpoint] = f"❌ FAIL ({response.status_code})"
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
            results[endpoint] = f"❌ ERROR ({e})"
    
    # Summary
    print("\n📊 Deployment Test Summary:")
    for endpoint, status in results.items():
        print(f"  {endpoint}: {status}")
    
    passed = sum(1 for status in results.values() if status.startswith("✅"))
    total = len(results)
    print(f"\n🎯 {passed}/{total} endpoints working")
    
    return passed == total

if __name__ == "__main__":
    # Default Render URL - replace with your actual URL after deployment
    render_url = "https://smite-divine-arsenal.onrender.com"
    
    print("Enter your Render app URL (or press Enter to use default):")
    url = input().strip() or render_url
    
    success = test_deployment(url)
    if success:
        print("\n🎉 Deployment successful! All systems operational.")
    else:
        print("\n⚠️  Some endpoints need attention.") 