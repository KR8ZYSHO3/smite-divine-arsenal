#!/usr/bin/env python3
"""
Test script for the new Playwright-based scraper
Verifies WebDriver process management and functionality
"""

import os
import sys
import psutil
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "divine_arsenal" / "backend"
sys.path.insert(0, str(backend_path))

def count_chrome_processes():
    """Count Chrome processes currently running."""
    chrome_processes = []
    for process in psutil.process_iter():
        try:
            if process.name() and 'chrome' in process.name().lower():
                chrome_processes.append({
                    'pid': process.pid,
                    'name': process.name(),
                    'memory_mb': process.memory_info().rss / (1024 * 1024)
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return chrome_processes

def test_playwright_scraper():
    """Test the new Playwright-based scraper."""
    
    print("🧪 TESTING PLAYWRIGHT SCRAPER")
    print("=" * 50)
    
    # Count Chrome processes before
    chrome_before = count_chrome_processes()
    print(f"📊 Chrome processes before test: {len(chrome_before)}")
    
    # Test import without triggering WebDriver
    print("\n🔍 Testing module import...")
    try:
        from scrapers import get_tracker_scraper
        print("✅ Successfully imported scraper module")
    except Exception as e:
        print(f"❌ Failed to import scraper module: {e}")
        return False
    
    # Count Chrome processes after import
    chrome_after_import = count_chrome_processes()
    print(f"📊 Chrome processes after import: {len(chrome_after_import)}")
    
    if len(chrome_after_import) > len(chrome_before):
        print(f"⚠️ WARNING: {len(chrome_after_import) - len(chrome_before)} new Chrome processes spawned during import!")
    else:
        print("✅ No new Chrome processes spawned during import")
    
    # Test scraper initialization
    print("\n🚀 Testing scraper initialization...")
    try:
        scraper = get_tracker_scraper(use_playwright=True, headless=True)
        if scraper:
            print("✅ Scraper initialized successfully")
        else:
            print("❌ Scraper initialization returned None")
            return False
    except Exception as e:
        print(f"❌ Scraper initialization failed: {e}")
        return False
    
    # Count Chrome processes after initialization
    chrome_after_init = count_chrome_processes()
    print(f"📊 Chrome processes after initialization: {len(chrome_after_init)}")
    
    if len(chrome_after_init) > len(chrome_after_import):
        print(f"⚠️ WARNING: {len(chrome_after_init) - len(chrome_after_import)} new Chrome processes spawned during initialization!")
    else:
        print("✅ No new Chrome processes spawned during initialization")
    
    # Test health check
    print("\n🏥 Testing health check...")
    try:
        health = scraper.get_health_check()
        print(f"✅ Health check successful: {health.get('status', 'unknown')}")
        print(f"   Response time: {health.get('response_time', 'N/A')} seconds")
        print(f"   Playwright status: {health.get('playwright_status', 'N/A')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Count Chrome processes after health check
    chrome_after_health = count_chrome_processes()
    print(f"📊 Chrome processes after health check: {len(chrome_after_health)}")
    
    # Test basic functionality (without actually scraping)
    print("\n🎯 Testing basic functionality...")
    try:
        # This should not spawn processes since we're not actually scraping
        test_result = scraper.get_player_profile("nonexistent_user_test")
        print(f"✅ Basic functionality test completed (result: {test_result is not None})")
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
    
    # Final Chrome process count
    chrome_final = count_chrome_processes()
    print(f"📊 Chrome processes after all tests: {len(chrome_final)}")
    
    # Clean up
    print("\n🧹 Cleaning up...")
    try:
        if hasattr(scraper, 'close'):
            scraper.close()
            print("✅ Scraper closed successfully")
        
        # Also test the global cleanup
        from scrapers import close_all_scrapers
        close_all_scrapers()
        print("✅ All scrapers closed successfully")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")
    
    # Final final Chrome process count
    chrome_cleanup = count_chrome_processes()
    print(f"📊 Chrome processes after cleanup: {len(chrome_cleanup)}")
    
    # Summary
    print("\n📋 SUMMARY:")
    print(f"   Initial Chrome processes: {len(chrome_before)}")
    print(f"   After import: {len(chrome_after_import)} (diff: {len(chrome_after_import) - len(chrome_before)})")
    print(f"   After init: {len(chrome_after_init)} (diff: {len(chrome_after_init) - len(chrome_after_import)})")
    print(f"   After health check: {len(chrome_after_health)} (diff: {len(chrome_after_health) - len(chrome_after_init)})")
    print(f"   After tests: {len(chrome_final)} (diff: {len(chrome_final) - len(chrome_after_health)})")
    print(f"   After cleanup: {len(chrome_cleanup)} (diff: {len(chrome_cleanup) - len(chrome_final)})")
    
    total_spawned = len(chrome_cleanup) - len(chrome_before)
    if total_spawned <= 0:
        print("🎉 SUCCESS: No net Chrome processes spawned!")
        return True
    elif total_spawned <= 2:
        print("✅ GOOD: Only minimal Chrome processes spawned (acceptable)")
        return True
    else:
        print(f"⚠️ WARNING: {total_spawned} Chrome processes spawned (needs improvement)")
        return False

def test_lazy_loading():
    """Test that lazy loading prevents immediate WebDriver spawning."""
    
    print("\n🔄 TESTING LAZY LOADING")
    print("=" * 50)
    
    # Count Chrome processes before
    chrome_before = count_chrome_processes()
    print(f"📊 Chrome processes before lazy loading test: {len(chrome_before)}")
    
    # Import the module
    try:
        from scrapers import TrackerScraper, get_all_scrapers
        print("✅ Imported lazy loading module")
    except Exception as e:
        print(f"❌ Failed to import lazy loading module: {e}")
        return False
    
    # Count Chrome processes after import
    chrome_after_import = count_chrome_processes()
    print(f"📊 Chrome processes after import: {len(chrome_after_import)}")
    
    if len(chrome_after_import) > len(chrome_before):
        print(f"❌ FAIL: {len(chrome_after_import) - len(chrome_before)} Chrome processes spawned during import!")
        return False
    else:
        print("✅ SUCCESS: No Chrome processes spawned during import")
    
    # Test get_all_scrapers (should not spawn processes)
    try:
        scrapers = get_all_scrapers()
        print(f"✅ get_all_scrapers() returned {len(scrapers)} scrapers")
    except Exception as e:
        print(f"❌ get_all_scrapers() failed: {e}")
        return False
    
    # Count Chrome processes after get_all_scrapers
    chrome_after_get_all = count_chrome_processes()
    print(f"📊 Chrome processes after get_all_scrapers(): {len(chrome_after_get_all)}")
    
    if len(chrome_after_get_all) > len(chrome_after_import):
        print(f"❌ FAIL: {len(chrome_after_get_all) - len(chrome_after_import)} Chrome processes spawned during get_all_scrapers!")
        return False
    else:
        print("✅ SUCCESS: No Chrome processes spawned during get_all_scrapers")
    
    return True

if __name__ == "__main__":
    print("🧪 SMITE 2 DIVINE ARSENAL - PLAYWRIGHT SCRAPER TEST")
    print("=" * 60)
    
    # Test lazy loading first
    lazy_success = test_lazy_loading()
    
    # Test the actual scraper
    scraper_success = test_playwright_scraper()
    
    print("\n" + "=" * 60)
    if lazy_success and scraper_success:
        print("🎉 ALL TESTS PASSED!")
        print("   WebDriver process management is working correctly")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("   WebDriver process management needs improvement")
        sys.exit(1) 