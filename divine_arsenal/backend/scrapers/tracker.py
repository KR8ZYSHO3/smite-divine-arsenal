"""Enhanced Scraper for Tracker.gg Smite 2 stats."""

import json
import logging
import re
import time
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class TrackerScraper:
    """Enhanced scraper for Tracker.gg Smite 2 player statistics and match data."""

    def __init__(self, use_selenium: bool = True) -> None:
        """Initialize the scraper.
        
        Args:
            use_selenium: Whether to use Selenium for dynamic content (default: True)
        """
        self.base_url = "https://tracker.gg/smite2"
        self.use_selenium = use_selenium
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
            'Referer': 'https://tracker.gg/',
        })
        
        if use_selenium:
            self._setup_selenium()
        else:
            self.driver = None

    def _setup_selenium(self):
        """Setup Selenium WebDriver for dynamic content."""
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Suppress logging and disable problematic features
        self.options.add_argument("--disable-logging")
        self.options.add_argument("--log-level=3")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-plugins")
        self.options.add_argument("--disable-background-timer-throttling")
        self.options.add_argument("--disable-backgrounding-occluded-windows")
        self.options.add_argument("--disable-renderer-backgrounding")
        self.options.add_argument("--disable-features=TranslateUI")
        self.options.add_argument("--disable-ipc-flooding-protection")
        
        # Experimental options to suppress Chrome messages
        self.options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option('prefs', {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0,
            'profile.managed_default_content_settings.images': 2
        })

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            logger.warning(f"Failed to setup Selenium, falling back to requests: {e}")
            self.driver = None
            self.use_selenium = False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, Exception)),
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
            if self.use_selenium and self.driver:
                return self._get_player_profile_selenium(player_name)
            else:
                return self._get_player_profile_requests(player_name)
        except Exception as e:
            logger.warning(f"Error fetching player profile for {player_name}: {e}")
            return None

    def _get_player_profile_selenium(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get player profile using Selenium for dynamic content."""
        try:
            # Navigate to player profile
            encoded_name = quote_plus(player_name)
            profile_url = f"{self.base_url}/profile/{encoded_name}"
            self.driver.get(profile_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)  # Additional wait for dynamic content
            
            # Extract profile data
            profile_data = {
                "player_name": player_name,
                "profile_url": profile_url,
                "stats": {},
                "recent_matches": [],
                "favorite_gods": [],
                "ranked_stats": {}
            }
            
            # Get basic stats
            try:
                stat_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='stat-value'], .stat-value, .value")
                for element in stat_elements:
                    try:
                        label = element.get_attribute("data-testid") or element.get_attribute("aria-label") or "Unknown"
                        value = element.text.strip()
                        if value:
                            profile_data["stats"][label] = value
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"Could not extract stats: {e}")
            
            # Get recent matches
            try:
                match_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='match-row'], .match-row, .game-row")
                for element in match_elements[:10]:  # Last 10 matches
                    try:
                        match_data = self._extract_match_data(element)
                        if match_data:
                            profile_data["recent_matches"].append(match_data)
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"Could not extract recent matches: {e}")
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Selenium error for {player_name}: {e}")
            return None

    def _get_player_profile_requests(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get player profile using requests (fallback method)."""
        try:
            # Add delay to be more human-like
            time.sleep(1)
            
            encoded_name = quote_plus(player_name)
            profile_url = f"{self.base_url}/profile/{encoded_name}"
            
            # Add retry mechanism
            for attempt in range(3):
                try:
                    response = self.session.get(profile_url, timeout=15)
                    if response.status_code == 403:
                        logger.warning(f"403 Forbidden on attempt {attempt + 1}, retrying...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
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
                "ranked_stats": {}
            }
            
            # Extract basic stats from HTML
            stat_elements = soup.find_all(["div", "span"], class_=re.compile(r"stat|value|metric"))
            for element in stat_elements:
                try:
                    label = element.get("data-testid") or element.get("aria-label") or element.get_text().strip()
                    value = element.get_text().strip()
                    if value and label:
                        profile_data["stats"][label] = value
                except Exception:
                    continue
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Requests error for {player_name}: {e}")
            return None

    def get_recent_matches(self, player_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent match history for a player.
        
        Args:
            player_name: The player's username
            limit: Maximum number of matches to retrieve
            
        Returns:
            List of match data dictionaries
        """
        try:
            if self.use_selenium and self.driver:
                return self._get_recent_matches_selenium(player_name, limit)
            else:
                return self._get_recent_matches_requests(player_name, limit)
        except Exception as e:
            logger.error(f"Error fetching recent matches for {player_name}: {e}")
            return []

    def _get_recent_matches_selenium(self, player_name: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent matches using Selenium."""
        try:
            encoded_name = quote_plus(player_name)
            matches_url = f"{self.base_url}/profile/{encoded_name}/matches"
            self.driver.get(matches_url)
            
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            matches = []
            match_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='match-row'], .match-row, .game-row")
            
            for element in match_elements[:limit]:
                try:
                    match_data = self._extract_match_data(element)
                    if match_data:
                        matches.append(match_data)
                except Exception as e:
                    logger.warning(f"Error extracting match data: {e}")
                    continue
            
            return matches
            
        except Exception as e:
            logger.error(f"Selenium error getting matches for {player_name}: {e}")
            return []

    def _get_recent_matches_requests(self, player_name: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent matches using requests."""
        try:
            encoded_name = quote_plus(player_name)
            matches_url = f"{self.base_url}/profile/{encoded_name}/matches"
            
            response = self.session.get(matches_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            matches = []
            
            match_elements = soup.find_all(["div", "tr"], class_=re.compile(r"match|game|row"))
            
            for element in match_elements[:limit]:
                try:
                    match_data = self._extract_match_data_from_html(element)
                    if match_data:
                        matches.append(match_data)
                except Exception as e:
                    logger.warning(f"Error extracting match data from HTML: {e}")
                    continue
            
            return matches
            
        except Exception as e:
            logger.error(f"Requests error getting matches for {player_name}: {e}")
            return []

    def _extract_match_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract match data from a Selenium element."""
        try:
            match_data = {
                "match_id": element.get_attribute("data-match-id") or "",
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
            
            # Extract text content and try to parse
            text_content = element.text
            
            # Try to extract god name
            god_match = re.search(r'([A-Z][a-z]+)', text_content)
            if god_match:
                match_data["god_name"] = god_match.group(1)
            
            # Try to extract KDA
            kda_match = re.search(r'(\d+)/(\d+)/(\d+)', text_content)
            if kda_match:
                match_data["kills"] = int(kda_match.group(1))
                match_data["deaths"] = int(kda_match.group(2))
                match_data["assists"] = int(kda_match.group(3))
            
            # Try to extract result
            if "WIN" in text_content.upper():
                match_data["result"] = "WIN"
            elif "LOSS" in text_content.upper():
                match_data["result"] = "LOSS"
            
            return match_data
            
        except Exception as e:
            logger.warning(f"Error extracting match data: {e}")
            return None

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
            
            # Similar extraction logic as Selenium version
            god_match = re.search(r'([A-Z][a-z]+)', text_content)
            if god_match:
                match_data["god_name"] = god_match.group(1)
            
            kda_match = re.search(r'(\d+)/(\d+)/(\d+)', text_content)
            if kda_match:
                match_data["kills"] = int(kda_match.group(1))
                match_data["deaths"] = int(kda_match.group(2))
                match_data["assists"] = int(kda_match.group(3))
            
            if "WIN" in text_content.upper():
                match_data["result"] = "WIN"
            elif "LOSS" in text_content.upper():
                match_data["result"] = "LOSS"
            
            return match_data
            
        except Exception as e:
            logger.warning(f"Error extracting match data from HTML: {e}")
            return None

    def get_leaderboard(self, category: str = "kills", platform: str = "pc") -> List[Dict[str, str]]:
        """Get leaderboard data from Tracker.gg.
        
        Args:
            category: The leaderboard category (kills, wins, damage, etc.)
            platform: Platform filter (pc, xbox, ps4)
            
        Returns:
            List of leaderboard entries
        """
        try:
            if self.use_selenium and self.driver:
                return self._get_leaderboard_selenium(category, platform)
            else:
                return self._get_leaderboard_requests(category, platform)
        except Exception as e:
            logger.error(f"Error fetching leaderboard for {category}: {e}")
            return []

    def _get_leaderboard_selenium(self, category: str, platform: str) -> List[Dict[str, str]]:
        """Get leaderboard using Selenium."""
        try:
            leaderboard_url = f"{self.base_url}/leaderboards/{category}?platform={platform}"
            self.driver.get(leaderboard_url)
            
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            leaderboard = []
            rows = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='leaderboard-row'], .leaderboard-row, .row")
            
            for row in rows:
                try:
                    rank = row.find_element(By.CSS_SELECTOR, "[data-testid='rank'], .rank").text
                    player = row.find_element(By.CSS_SELECTOR, "[data-testid='player'], .player").text
                    value = row.find_element(By.CSS_SELECTOR, "[data-testid='value'], .value").text
                    
                    leaderboard.append({
                        "rank": rank,
                        "player": player,
                        "value": value,
                        "category": category,
                        "platform": platform
                    })
                except Exception as e:
                    logger.warning(f"Error extracting leaderboard row: {e}")
                    continue
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Selenium error getting leaderboard: {e}")
            return []

    def _get_leaderboard_requests(self, category: str, platform: str) -> List[Dict[str, str]]:
        """Get leaderboard using requests."""
        try:
            leaderboard_url = f"{self.base_url}/leaderboards/{category}?platform={platform}"
            
            response = self.session.get(leaderboard_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            leaderboard = []
            
            rows = soup.find_all(["div", "tr"], class_=re.compile(r"leaderboard|row"))
            
            for row in rows:
                try:
                    rank_elem = row.find(class_=re.compile(r"rank"))
                    player_elem = row.find(class_=re.compile(r"player"))
                    value_elem = row.find(class_=re.compile(r"value"))
                    
                    if rank_elem and player_elem and value_elem:
                        leaderboard.append({
                            "rank": rank_elem.get_text().strip(),
                            "player": player_elem.get_text().strip(),
                            "value": value_elem.get_text().strip(),
                            "category": category,
                            "platform": platform
                        })
                except Exception as e:
                    logger.warning(f"Error extracting leaderboard row from HTML: {e}")
                    continue
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Requests error getting leaderboard: {e}")
            return []

    def search_players(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """Search for players by name.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of player search results
        """
        try:
            search_url = f"{self.base_url}/search?q={quote_plus(query)}"
            
            if self.use_selenium and self.driver:
                return self._search_players_selenium(search_url, limit)
            else:
                return self._search_players_requests(search_url, limit)
        except Exception as e:
            logger.error(f"Error searching players for '{query}': {e}")
            return []

    def _search_players_selenium(self, search_url: str, limit: int) -> List[Dict[str, str]]:
        """Search players using Selenium."""
        try:
            self.driver.get(search_url)
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            results = []
            player_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='player-result'], .player-result, .result")
            
            for element in player_elements[:limit]:
                try:
                    name = element.find_element(By.CSS_SELECTOR, "[data-testid='player-name'], .player-name").text
                    platform = element.find_element(By.CSS_SELECTOR, "[data-testid='platform'], .platform").text
                    
                    results.append({
                        "name": name,
                        "platform": platform
                    })
                except Exception as e:
                    logger.warning(f"Error extracting player result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Selenium error searching players: {e}")
            return []

    def _search_players_requests(self, search_url: str, limit: int) -> List[Dict[str, str]]:
        """Search players using requests."""
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            player_elements = soup.find_all(["div", "a"], class_=re.compile(r"player|result"))
            
            for element in player_elements[:limit]:
                try:
                    name_elem = element.find(class_=re.compile(r"name"))
                    platform_elem = element.find(class_=re.compile(r"platform"))
                    
                    if name_elem:
                        results.append({
                            "name": name_elem.get_text().strip(),
                            "platform": platform_elem.get_text().strip() if platform_elem else "Unknown"
                        })
                except Exception as e:
                    logger.warning(f"Error extracting player result from HTML: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Requests error searching players: {e}")
            return []

    def __del__(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        if hasattr(self, 'session'):
            try:
                self.session.close()
            except Exception:
                pass
