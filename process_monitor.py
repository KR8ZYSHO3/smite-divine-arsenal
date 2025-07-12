#!/usr/bin/env python3
"""
Process Monitor for SMITE 2 Divine Arsenal
Monitors and cleans up WebDriver processes to prevent spam
"""

import subprocess
import time
import psutil
import logging
from typing import List, Dict, Any
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_webdriver_chrome(process):
    """Check if a Chrome process is likely a WebDriver process"""
    try:
        cmdline = process.cmdline()
        if not cmdline:
            return False
            
        # Look for WebDriver-specific command line arguments
        webdriver_indicators = [
            '--remote-debugging-port=',
            '--test-type=webdriver',
            '--disable-extensions',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--headless',
            '--user-data-dir=',
            '--port='
        ]
        
        cmdline_str = ' '.join(cmdline)
        
        # Check if it has multiple WebDriver indicators
        indicator_count = sum(1 for indicator in webdriver_indicators if indicator in cmdline_str)
        
        # Also check for common WebDriver patterns
        if indicator_count >= 2:  # Multiple indicators suggest WebDriver
            return True
            
        # Check for specific WebDriver patterns
        if ('--remote-debugging-port=' in cmdline_str and 
            ('--test-type' in cmdline_str or '--disable-extensions' in cmdline_str)):
            return True
            
        return False
        
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False

def monitor_webdriver_processes():
    """Monitor and optionally kill WebDriver Chrome processes"""
    webdriver_processes = []
    regular_chrome_processes = []
    
    for process in psutil.process_iter():
        try:
            if process.name() and 'chrome' in process.name().lower():
                if is_webdriver_chrome(process):
                    webdriver_processes.append(process)
                else:
                    regular_chrome_processes.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    logger.info(f"Found {len(webdriver_processes)} WebDriver Chrome processes")
    logger.info(f"Found {len(regular_chrome_processes)} regular Chrome processes (will NOT touch these)")
    
    if webdriver_processes:
        total_memory = sum(p.memory_info().rss for p in webdriver_processes) / (1024 * 1024)  # MB
        logger.info(f"WebDriver processes using {total_memory:.2f} MB memory")
        
        print("\nWebDriver Chrome processes found:")
        for i, process in enumerate(webdriver_processes, 1):
            memory_mb = process.memory_info().rss / (1024 * 1024)
            cmdline = ' '.join(process.cmdline()[:3])  # Show first 3 parts of command line
            print(f"{i}. PID: {process.pid}, Memory: {memory_mb:.2f} MB")
            print(f"   Command: {cmdline}...")
        
        print(f"\nRegular Chrome processes (will NOT be touched): {len(regular_chrome_processes)}")
        
        choice = input("\nDo you want to kill ONLY the WebDriver Chrome processes? (y/n): ").lower()
        if choice == 'y':
            killed_count = 0
            for process in webdriver_processes:
                try:
                    process.terminate()
                    killed_count += 1
                    logger.info(f"Terminated WebDriver process PID: {process.pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    logger.warning(f"Could not terminate process PID: {process.pid}")
            
            logger.info(f"Killed {killed_count} WebDriver Chrome processes")
            logger.info(f"Your regular Chrome browsers remain untouched")
        else:
            logger.info("No processes killed")
    else:
        logger.info("No WebDriver Chrome processes found")


if __name__ == "__main__":
    monitor_webdriver_processes() 