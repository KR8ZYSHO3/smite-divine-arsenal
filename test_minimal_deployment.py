#!/usr/bin/env python3
"""
Test script for minimal Divine Arsenal deployment
"""

import requests
import time

def test_minimal_deployment():
    """Test the minimal app deployment"""
    base_url = "https://smite-divine-arsenal.onrender.com"
    
    print("🧪 Testing Minimal Divine Arsenal Deployment")
    print(f"🔗 URL: {base_url}")
    print()
    
    # Test endpoints
    endpoints = {
        "/": "Home page",
        "/health": "Health check",
        "/api/test": "API test endpoint"
    }
    
    results = {}
    for endpoint, description in endpoints.items():
        try:
            print(f"Testing {endpoint} ({description})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: SUCCESS")
                if 'message' in data:
                    print(f"   Message: {data['message']}")
                results[endpoint] = "✅ PASS"
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
                results[endpoint] = f"❌ FAIL ({response.status_code})"
                
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {e}")
            results[endpoint] = f"❌ ERROR ({e})"
        
        print()
    
    # Summary
    print("📊 Test Results:")
    for endpoint, status in results.items():
        print(f"  {endpoint}: {status}")
    
    passed = sum(1 for status in results.values() if status.startswith("✅"))
    total = len(results)
    
    if passed == total:
        print(f"\n🎉 SUCCESS! All {total} endpoints working")
        print("✅ Minimal deployment is functional")
        return True
    else:
        print(f"\n⚠️  {passed}/{total} endpoints working")
        return False

if __name__ == "__main__":
    success = test_minimal_deployment()
    if success:
        print("\n🚀 Ready to deploy full app!")
    else:
        print("\n🔧 Need to fix issues first.") 