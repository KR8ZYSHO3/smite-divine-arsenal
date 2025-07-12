"""
Enhanced Playwright-based Tracker.gg Scraper for SMITE 2 Divine Arsenal
Replaces Selenium with Playwright for better reliability and performance
"""

import asyncio
import json
import logging
import re
import time
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page, Browser
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class TrackerPlaywrightScraper:
    """Enhanced Playwright-based scraper for Tracker.gg SMITE 2 statistics."""

    def __init__(self, use_playwright: bool = True, headless: bool = True) -> None:
        """Initialize the scraper.
        
        Args:
            use_playwright: Whether to use Playwright for dynamic content
            headless: Whether to run browser in headless mode
        """
        self.base_url = "https://tracker.gg/smite2"
        self.use_playwright = use_playwright
        self.headless = headless
        self.session = requests.Session()
        
        # Enhanced headers to bypass detection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })

    def _get_browser_context(self, playwright):
        """Create a new browser context with stealth settings."""
        try:
            # Launch browser with stealth settings
            browser = playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-logging',
                    '--log-level=3',
                    '--disable-ipc-flooding-protection',
                ]
            )
            
            # Create context with additional stealth settings
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True,
                bypass_csp=True,
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
            
            return browser, context
            
        except Exception as e:
            logger.error(f"Error creating browser context: {e}")
            return None, None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=5, max=30),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def get_player_profile(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive player profile from Tracker.gg.
        
        Args:
            player_name: The player's username to look up
            
        Returns:
            Dictionary containing player profile data or None if not found
        """
        try:
            logger.info(f"Fetching profile for player: {player_name}")
            
            if self.use_playwright:
                return self._get_player_profile_playwright(player_name)
            else:
                return self._get_player_profile_requests(player_name)
                
        except Exception as e:
            logger.warning(f"Error fetching player profile for {player_name}: {e}")
            return None

    def _get_player_profile_playwright(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get player profile using Playwright for dynamic content."""
        try:
            with sync_playwright() as p:
                browser, context = self._get_browser_context(p)
                if not browser or not context:
                    logger.error("Failed to create browser context")
                    return None
                
                try:
                    page = context.new_page()
                    
                    # Navigate to player profile
                    encoded_name = quote_plus(player_name)
                    profile_url = f"{self.base_url}/profile/{encoded_name}"
                    
                    logger.info(f"Navigating to: {profile_url}")
                    
                    # Navigate with timeout and wait for load
                    page.goto(profile_url, timeout=30000, wait_until='networkidle')
                    
                    # Wait for page content to load
                    page.wait_for_timeout(3000)
                    
                    # Check if profile exists (look for error messages)
                    if page.locator("text=not found").count() > 0 or page.locator("text=404").count() > 0:
                        logger.warning(f"Profile not found for player: {player_name}")
                        return None
                    
                    # Extract profile data
                    profile_data = {
                        "player_name": player_name,
                        "profile_url": profile_url,
                        "stats": {},
                        "recent_matches": [],
                        "favorite_gods": [],
                        "ranked_stats": {},
                        "scraped_at": time.time()
                    }
                    
                    # Extract basic stats with multiple selectors
                    try:
                        stat_selectors = [
                            '[data-testid*="stat"]',
                            '.stat-value',
                            '.value',
                            '.metric-value',
                            '.number'
                        ]
                        
                        for selector in stat_selectors:
                            elements = page.locator(selector).all()
                            for element in elements:
                                try:
                                    text = element.inner_text().strip()
                                    if text and text.replace(',', '').replace('.', '').isdigit():
                                        # Try to find associated label
                                        parent = element.locator('..').first
                                        label = parent.inner_text().strip()
                                        if label and label != text:
                                            profile_data["stats"][label] = text
                                except Exception:
                                    continue
                                    
                    except Exception as e:
                        logger.warning(f"Could not extract stats: {e}")
                    
                    # Extract recent matches
                    try:
                        match_selectors = [
                            '[data-testid*="match"]',
                            '.match-row',
                            '.game-row',
                            '.match-item'
                        ]
                        
                        for selector in match_selectors:
                            elements = page.locator(selector).all()
                            if elements:
                                for element in elements[:10]:  # Last 10 matches
                                    try:
                                        match_data = self._extract_match_data_playwright(element)
                                        if match_data:
                                            profile_data["recent_matches"].append(match_data)
                                    except Exception:
                                        continue
                                break  # Found matches, no need to try other selectors
                                
                    except Exception as e:
                        logger.warning(f"Could not extract recent matches: {e}")
                    
                    # Extract favorite gods
                    try:
                        god_selectors = [
                            '[data-testid*="god"]',
                            '.god-name',
                            '.character-name',
                            '.champion-name'
                        ]
                        
                        for selector in god_selectors:
                            elements = page.locator(selector).all()
                            if elements:
                                for element in elements[:5]:  # Top 5 gods
                                    try:
                                        god_name = element.inner_text().strip()
                                        if god_name:
                                            profile_data["favorite_gods"].append(god_name)
                                    except Exception:
                                        continue
                                break
                                
                    except Exception as e:
                        logger.warning(f"Could not extract favorite gods: {e}")
                    
                    logger.info(f"Successfully scraped profile for {player_name}")
                    return profile_data
                    
                finally:
                    # Always clean up
                    try:
                        context.close()
                        browser.close()
                    except Exception as e:
                        logger.warning(f"Error closing browser: {e}")
                        
        except Exception as e:
            logger.error(f"Playwright error for {player_name}: {e}")
            return None

    def _get_player_profile_requests(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get player profile using requests (fallback method)."""
        try:
            encoded_name = quote_plus(player_name)
            profile_url = f"{self.base_url}/profile/{encoded_name}"
            
            logger.info(f"Fetching profile via requests: {profile_url}")
            
            # Retry mechanism with exponential backoff
            for attempt in range(3):
                try:
                    response = self.session.get(profile_url, timeout=15)
                    
                    if response.status_code == 403:
                        logger.warning(f"403 Forbidden on attempt {attempt + 1}, retrying...")
                        time.sleep(2 ** attempt)
                        continue
                    elif response.status_code == 404:
                        logger.warning(f"Player not found: {player_name}")
                        return None
                        
                    response.raise_for_status()
                    break
                    
                except requests.exceptions.RequestException as e:
                    if attempt == 2:  # Last attempt
                        raise e
                    logger.warning(f"Request failed on attempt {attempt + 1}: {e}")
                    time.sleep(2 ** attempt)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            profile_data = {
                "player_name": player_name,
                "profile_url": profile_url,
                "stats": {},
                "recent_matches": [],
                "favorite_gods": [],
                "ranked_stats": {},
                "scraped_at": time.time()
            }
            
            # Extract basic stats from HTML
            stat_patterns = [
                r'stats?["\']?\s*:\s*["\']?([^"\']+)["\']?',
                r'value["\']?\s*:\s*["\']?([^"\']+)["\']?',
                r'metric["\']?\s*:\s*["\']?([^"\']+)["\']?'
            ]
            
            for pattern in stat_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    if match.replace(',', '').replace('.', '').isdigit():
                        profile_data["stats"][f"stat_{len(profile_data['stats'])}"] = match
            
            logger.info(f"Successfully scraped profile for {player_name} via requests")
            return profile_data
            
        except Exception as e:
            logger.error(f"Requests error for {player_name}: {e}")
            return None

    def _extract_match_data_playwright(self, element) -> Optional[Dict[str, Any]]:
        """Extract match data from a Playwright element."""
        try:
            match_data = {
                "match_id": "",
                "god_name": "",
                "role": "",
                "result": "",
                "kills": 0,
                "deaths": 0,
                "assists": 0,
                "damage_dealt": 0,
                "damage_mitigated": 0,
                "gold_earned": 0,
                "items": [],
                "match_duration": 0,
                "game_mode": "",
                "timestamp": ""
            }
            
            # Extract text content
            text_content = element.inner_text()
            
            # Extract god name (look for capitalized words)
            god_match = re.search(r'([A-Z][a-z]+)', text_content)
            if god_match:
                match_data["god_name"] = god_match.group(1)
            
            # Extract KDA pattern
            kda_match = re.search(r'(\d+)/(\d+)/(\d+)', text_content)
            if kda_match:
                match_data["kills"] = int(kda_match.group(1))
                match_data["deaths"] = int(kda_match.group(2))
                match_data["assists"] = int(kda_match.group(3))
            
            # Extract result
            if "WIN" in text_content.upper() or "VICTORY" in text_content.upper():
                match_data["result"] = "WIN"
            elif "LOSS" in text_content.upper() or "DEFEAT" in text_content.upper():
                match_data["result"] = "LOSS"
            
            # Extract damage numbers
            damage_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*damage', text_content, re.IGNORECASE)
            if damage_match:
                match_data["damage_dealt"] = int(damage_match.group(1).replace(',', ''))
            
            return match_data
            
        except Exception as e:
            logger.warning(f"Error extracting match data: {e}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=5, max=30),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def get_recent_matches(self, player_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent match history for a player.
        
        Args:
            player_name: The player's username
            limit: Maximum number of matches to retrieve
            
        Returns:
            List of match data dictionaries
        """
        try:
            logger.info(f"Fetching recent matches for: {player_name}")
            
            if self.use_playwright:
                return self._get_recent_matches_playwright(player_name, limit)
            else:
                return self._get_recent_matches_requests(player_name, limit)
                
        except Exception as e:
            logger.error(f"Error fetching recent matches for {player_name}: {e}")
            return []

    def _get_recent_matches_playwright(self, player_name: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent matches using Playwright."""
        try:
            with sync_playwright() as p:
                browser, context = self._get_browser_context(p)
                if not browser or not context:
                    return []
                
                try:
                    page = context.new_page()
                    
                    encoded_name = quote_plus(player_name)
                    matches_url = f"{self.base_url}/profile/{encoded_name}/matches"
                    
                    page.goto(matches_url, timeout=30000, wait_until='networkidle')
                    page.wait_for_timeout(3000)
                    
                    matches = []
                    match_selectors = [
                        '[data-testid*="match"]',
                        '.match-row',
                        '.game-row',
                        '.match-item'
                    ]
                    
                    for selector in match_selectors:
                        elements = page.locator(selector).all()
                        if elements:
                            for element in elements[:limit]:
                                try:
                                    match_data = self._extract_match_data_playwright(element)
                                    if match_data:
                                        matches.append(match_data)
                                except Exception as e:
                                    logger.warning(f"Error extracting match data: {e}")
                                    continue
                            break
                    
                    logger.info(f"Found {len(matches)} recent matches for {player_name}")
                    return matches
                    
                finally:
                    try:
                        context.close()
                        browser.close()
                    except Exception as e:
                        logger.warning(f"Error closing browser: {e}")
                        
        except Exception as e:
            logger.error(f"Playwright error getting matches for {player_name}: {e}")
            return []

    def _get_recent_matches_requests(self, player_name: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent matches using requests."""
        try:
            encoded_name = quote_plus(player_name)
            matches_url = f"{self.base_url}/profile/{encoded_name}/matches"
            
            response = self.session.get(matches_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            matches = []
            
            # Look for match elements
            match_elements = soup.find_all(["div", "tr"], class_=re.compile(r"match|game|row"))
            
            for element in match_elements[:limit]:
                try:
                    match_data = self._extract_match_data_from_html(element)
                    if match_data:
                        matches.append(match_data)
                except Exception as e:
                    logger.warning(f"Error extracting match data from HTML: {e}")
                    continue
            
            logger.info(f"Found {len(matches)} recent matches for {player_name} via requests")
            return matches
            
        except Exception as e:
            logger.error(f"Requests error getting matches for {player_name}: {e}")
            return []

    def _extract_match_data_from_html(self, element) -> Optional[Dict[str, Any]]:
        """Extract match data from a BeautifulSoup element."""
        try:
            match_data = {
                "match_id": element.get("data-match-id", ""),
                "god_name": "",
                "role": "",
                "result": "",
                "kills": 0,
                "deaths": 0,
                "assists": 0,
                "damage_dealt": 0,
                "damage_mitigated": 0,
                "gold_earned": 0,
                "items": [],
                "match_duration": 0,
                "game_mode": "",
                "timestamp": ""
            }
            
            text_content = element.get_text()
            
            # Extract god name
            god_match = re.search(r'([A-Z][a-z]+)', text_content)
            if god_match:
                match_data["god_name"] = god_match.group(1)
            
            # Extract KDA
            kda_match = re.search(r'(\d+)/(\d+)/(\d+)', text_content)
            if kda_match:
                match_data["kills"] = int(kda_match.group(1))
                match_data["deaths"] = int(kda_match.group(2))
                match_data["assists"] = int(kda_match.group(3))
            
            # Extract result
            if "WIN" in text_content.upper() or "VICTORY" in text_content.upper():
                match_data["result"] = "WIN"
            elif "LOSS" in text_content.upper() or "DEFEAT" in text_content.upper():
                match_data["result"] = "LOSS"
            
            return match_data
            
        except Exception as e:
            logger.warning(f"Error extracting match data from HTML: {e}")
            return None

    def get_health_check(self) -> Dict[str, Any]:
        """Perform a health check of the scraper."""
        try:
            # Test basic connectivity
            response = self.session.get(self.base_url, timeout=10)
            
            health_data = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "playwright_available": self.use_playwright,
                "timestamp": time.time()
            }
            
            # Test Playwright if enabled
            if self.use_playwright:
                try:
                    with sync_playwright() as p:
                        browser, context = self._get_browser_context(p)
                        if browser and context:
                            try:
                                page = context.new_page()
                                page.goto(self.base_url, timeout=10000)
                                health_data["playwright_status"] = "working"
                            finally:
                                context.close()
                                browser.close()
                        else:
                            health_data["playwright_status"] = "failed"
                except Exception as e:
                    health_data["playwright_status"] = f"error: {e}"
            
            return health_data
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }

    def close(self):
        """Close the scraper and clean up resources."""
        try:
            self.session.close()
            logger.info("TrackerPlaywrightScraper closed successfully")
        except Exception as e:
            logger.warning(f"Error closing scraper: {e}")


# For backward compatibility
class TrackerScraper(TrackerPlaywrightScraper):
    """Alias for backward compatibility."""
    pass


if __name__ == "__main__":
    # Test the scraper
    scraper = TrackerPlaywrightScraper()
    
    # Test health check
    health = scraper.get_health_check()
    print(f"Health check: {health}")
    
    # Test profile fetching
    test_profile = scraper.get_player_profile("testuser")
    print(f"Test profile: {test_profile}")
    
    scraper.close() 