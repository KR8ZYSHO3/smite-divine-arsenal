#!/usr/bin/env python3
"""
Comprehensive Build Optimizer Test Suite
Tests all build optimization endpoints and functionality
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_GODS = ["Zeus", "Hecate", "Loki", "Athena", "Neith"]
TEST_ROLES = ["Mid", "Solo", "Support", "Carry", "Jungle"]
TEST_MODES = ["Conquest", "Arena", "Joust", "Assault"]

class BuildOptimizerTester:
    """Test suite for build optimizer functionality."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and data:
            print(f"   Response: {json.dumps(data, indent=2)}")
        print()
        
    def test_health_check(self) -> bool:
        """Test health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, f"Database: {data.get('database', 'unknown')}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unhealthy status: {data.get('status')}", data)
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
            
    def test_database_integrity(self) -> bool:
        """Test database integrity."""
        try:
            # Test gods endpoint
            response = self.session.get(f"{self.base_url}/api/gods")
            if response.status_code == 200:
                data = response.json()
                gods_count = data.get("count", 0)
                if gods_count >= 60:  # Expecting at least 60 gods
                    self.log_test("Database - Gods", True, f"Found {gods_count} gods")
                else:
                    self.log_test("Database - Gods", False, f"Only {gods_count} gods found, expected 60+")
                    return False
            else:
                self.log_test("Database - Gods", False, f"HTTP {response.status_code}")
                return False
                
            # Test items endpoint
            response = self.session.get(f"{self.base_url}/api/items")
            if response.status_code == 200:
                data = response.json()
                items_count = data.get("count", 0)
                if items_count >= 150:  # Expecting at least 150 items
                    self.log_test("Database - Items", True, f"Found {items_count} items")
                else:
                    self.log_test("Database - Items", False, f"Only {items_count} items found, expected 150+")
                    return False
            else:
                self.log_test("Database - Items", False, f"HTTP {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Database Integrity", False, f"Exception: {str(e)}")
            return False
            
    def test_basic_build_optimization(self) -> bool:
        """Test basic build optimization endpoint."""
        success_count = 0
        total_tests = 0
        
        for god in TEST_GODS[:3]:  # Test first 3 gods
            for role in TEST_ROLES[:3]:  # Test first 3 roles
                total_tests += 1
                try:
                    payload = {
                        "god": god,
                        "role": role,
                        "budget": 15000
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/optimize-build",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success") and data.get("build"):
                            build = data["build"]
                            items = build.get("items", [])
                            score = build.get("score", 0)
                            
                            if len(items) >= 4 and score > 0:
                                success_count += 1
                                self.log_test(
                                    f"Build Optimization - {god} ({role})", 
                                    True, 
                                    f"Generated {len(items)} items, score: {score}"
                                )
                            else:
                                self.log_test(
                                    f"Build Optimization - {god} ({role})", 
                                    False, 
                                    f"Insufficient items ({len(items)}) or score ({score})",
                                    data
                                )
                        else:
                            self.log_test(
                                f"Build Optimization - {god} ({role})", 
                                False, 
                                "No build in response",
                                data
                            )
                    else:
                        self.log_test(
                            f"Build Optimization - {god} ({role})", 
                            False, 
                            f"HTTP {response.status_code}",
                            response.text
                        )
                        
                except Exception as e:
                    self.log_test(
                        f"Build Optimization - {god} ({role})", 
                        False, 
                        f"Exception: {str(e)}"
                    )
                    
                # Rate limiting - small delay between requests
                time.sleep(0.1)
                
        success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
        overall_success = success_rate >= 70  # 70% success rate threshold
        
        self.log_test(
            "Basic Build Optimization Overall", 
            overall_success,
            f"Success rate: {success_rate:.1f}% ({success_count}/{total_tests})"
        )
        
        return overall_success
        
    def test_enhanced_build_optimization(self) -> bool:
        """Test enhanced build optimization endpoint."""
        try:
            payload = {
                "god": "Zeus",
                "role": "Mid",
                "mode": "Conquest",
                "player_name": "TestPlayer"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/optimize-build/enhanced",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("build") and data.get("explanation"):
                    self.log_test("Enhanced Build Optimization", True, "Enhanced optimization working")
                    return True
                else:
                    self.log_test("Enhanced Build Optimization", False, "Missing build or explanation", data)
                    return False
            else:
                self.log_test("Enhanced Build Optimization", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Enhanced Build Optimization", False, f"Exception: {str(e)}")
            return False
            
    def test_build_explanation(self) -> bool:
        """Test build explanation endpoint."""
        try:
            payload = {
                "god": "Zeus",
                "role": "Mid",
                "budget": 15000
            }
            
            response = self.session.post(
                f"{self.base_url}/api/explain-build",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("explanation"):
                    explanation_length = len(str(data["explanation"]))
                    self.log_test("Build Explanation", True, f"Generated {explanation_length} chars explanation")
                    return True
                else:
                    self.log_test("Build Explanation", False, "No explanation generated", data)
                    return False
            else:
                self.log_test("Build Explanation", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Build Explanation", False, f"Exception: {str(e)}")
            return False
            
    def test_statistical_analysis(self) -> bool:
        """Test statistical analysis endpoint."""
        try:
            payload = {
                "god": "Zeus",
                "role": "Mid",
                "simulations": 10  # Small number for testing
            }
            
            response = self.session.post(
                f"{self.base_url}/api/statistical-analysis",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("analysis_results"):
                    self.log_test("Statistical Analysis", True, "Monte Carlo simulation working")
                    return True
                else:
                    self.log_test("Statistical Analysis", False, "No analysis results", data)
                    return False
            else:
                self.log_test("Statistical Analysis", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Statistical Analysis", False, f"Exception: {str(e)}")
            return False
            
    def test_realtime_optimization(self) -> bool:
        """Test real-time optimization endpoint."""
        try:
            payload = {
                "god": "Zeus",
                "role": "Mid",
                "enemy_gods": ["Loki", "Neith"],
                "detected_items": {"Loki": ["Deathbringer"], "Neith": ["Devourer's Gauntlet"]},
                "budget": 15000,
                "playstyle": "meta"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/optimize-build/realtime",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("core_build"):
                    self.log_test("Real-time Optimization", True, "Real-time counter-building working")
                    return True
                else:
                    self.log_test("Real-time Optimization", False, "No core build generated", data)
                    return False
            else:
                self.log_test("Real-time Optimization", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Real-time Optimization", False, f"Exception: {str(e)}")
            return False
            
    def test_api_stats(self) -> bool:
        """Test API stats endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/api/stats")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    self.log_test("API Stats", True, f"Stats returned: {list(data.keys())}")
                    return True
                else:
                    self.log_test("API Stats", False, "Empty stats response", data)
                    return False
            else:
                self.log_test("API Stats", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("API Stats", False, f"Exception: {str(e)}")
            return False
            
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("🧪 STARTING COMPREHENSIVE BUILD OPTIMIZER TESTS")
        print("=" * 60)
        
        test_methods = [
            ("Health Check", self.test_health_check),
            ("Database Integrity", self.test_database_integrity),
            ("Basic Build Optimization", self.test_basic_build_optimization),
            ("Enhanced Build Optimization", self.test_enhanced_build_optimization),
            ("Build Explanation", self.test_build_explanation),
            ("Statistical Analysis", self.test_statistical_analysis),
            ("Real-time Optimization", self.test_realtime_optimization),
            ("API Stats", self.test_api_stats),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_method in test_methods:
            print(f"Running {test_name}...")
            try:
                success = test_method()
                if success:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test_name} - Exception: {str(e)}")
                failed += 1
                
        print("=" * 60)
        print(f"📊 TEST RESULTS SUMMARY")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Total: {passed + failed}")
        print(f"   Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if passed >= 6:  # Need at least 6/8 tests to pass
            print("✅ BUILD OPTIMIZER READY FOR DEPLOYMENT")
        else:
            print("❌ BUILD OPTIMIZER NEEDS FIXES BEFORE DEPLOYMENT")
            
        return {
            "passed": passed,
            "failed": failed,
            "total": passed + failed,
            "success_rate": (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0,
            "ready_for_deployment": passed >= 6,
            "detailed_results": self.test_results
        }

def main():
    """Main test execution."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
        
    print(f"Testing against: {base_url}")
    
    tester = BuildOptimizerTester(base_url)
    results = tester.run_all_tests()
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\n📁 Detailed results saved to: test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if results["ready_for_deployment"] else 1)

if __name__ == "__main__":
    main() 