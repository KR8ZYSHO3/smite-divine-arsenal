#!/usr/bin/env python3
"""
Test script for SMITE 2 Divine Arsenal Community Features
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/community"

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_online_users():
    """Test getting online users."""
    print("\n👥 Testing online users...")
    try:
        response = requests.get(f"{API_BASE}/users/online")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Online users: {data['count']} users online")
            return True
        else:
            print(f"❌ Failed to get online users: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Online users error: {e}")
        return False

def test_community_stats():
    """Test getting community statistics."""
    print("\n📊 Testing community stats...")
    try:
        response = requests.get(f"{API_BASE}/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data['stats']
            print(f"✅ Community stats:")
            print(f"   - Total users: {stats['total_users']}")
            print(f"   - Online users: {stats['online_users']}")
            print(f"   - Online percentage: {stats['online_percentage']}%")
            print(f"   - Active parties: {stats['active_parties']}")
            print(f"   - Recent messages: {stats['recent_messages']}")
            return True
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return False

def test_public_parties():
    """Test getting public parties."""
    print("\n🎯 Testing public parties...")
    try:
        response = requests.get(f"{API_BASE}/parties")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Public parties: {data['count']} parties available")
            return True
        else:
            print(f"❌ Failed to get parties: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Parties error: {e}")
        return False

def test_chat_messages():
    """Test getting chat messages."""
    print("\n💬 Testing chat messages...")
    try:
        response = requests.get(f"{API_BASE}/chat/messages/global")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat messages: {len(data['messages'])} messages in global chat")
            return True
        else:
            print(f"❌ Failed to get chat messages: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def test_user_search():
    """Test user search functionality."""
    print("\n🔍 Testing user search...")
    try:
        response = requests.get(f"{API_BASE}/users/search?q=test")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User search: Found {len(data['users'])} users matching 'test'")
            return True
        else:
            print(f"❌ Failed to search users: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

def test_authentication_flow():
    """Test the authentication flow with a mock user."""
    print("\n🔐 Testing authentication flow...")
    
    # Test login with invalid user (should fail gracefully)
    try:
        response = requests.post(f"{API_BASE}/auth/login", 
                               json={"tracker_username": "nonexistent_user_12345"})
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Authentication properly rejected invalid user: {data.get('error', 'Unknown error')}")
            return True
        else:
            print(f"❌ Unexpected response for invalid user: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints are accessible."""
    print("\n🌐 Testing API endpoint accessibility...")
    
    endpoints = [
        ("GET", "/users/online"),
        ("GET", "/users/search?q=test"),
        ("GET", "/parties"),
        ("GET", "/chat/messages/global"),
        ("GET", "/stats"),
        ("GET", "/health"),
    ]
    
    success_count = 0
    for method, endpoint in endpoints:
        try:
            url = f"{API_BASE}{endpoint}"
            response = requests.request(method, url)
            if response.status_code in [200, 400, 401]:  # Acceptable responses
                print(f"✅ {method} {endpoint}: {response.status_code}")
                success_count += 1
            else:
                print(f"❌ {method} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint}: Error - {e}")
    
    print(f"\n📈 API endpoint test results: {success_count}/{len(endpoints)} endpoints accessible")
    return success_count == len(endpoints)

def test_database_connectivity():
    """Test database connectivity and table creation."""
    print("\n🗄️ Testing database connectivity...")
    try:
        # Test that we can get stats (which requires database access)
        response = requests.get(f"{API_BASE}/stats")
        if response.status_code == 200:
            print("✅ Database connectivity confirmed")
            return True
        else:
            print(f"❌ Database connectivity failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def main():
    """Run all community feature tests."""
    print("🎮 SMITE 2 Divine Arsenal - Community Features Test")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Database Connectivity", test_database_connectivity),
        ("Online Users", test_online_users),
        ("Community Stats", test_community_stats),
        ("Public Parties", test_public_parties),
        ("Chat Messages", test_chat_messages),
        ("User Search", test_user_search),
        ("Authentication Flow", test_authentication_flow),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Community features are working correctly.")
        print("\n🚀 Next steps:")
        print("1. Visit http://localhost:5000/community to access the dashboard")
        print("2. Try logging in with a valid Tracker.gg SMITE 2 username")
        print("3. Explore the chat, parties, and community features")
    else:
        print("⚠️ Some tests failed. Check the server logs for more details.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure the Flask server is running: python app.py")
        print("2. Check that all dependencies are installed: pip install -r requirements.txt")
        print("3. Verify database permissions and connectivity")
        print("4. Check the server logs for error messages")

if __name__ == "__main__":
    main() 