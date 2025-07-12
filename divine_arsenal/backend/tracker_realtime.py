#!/usr/bin/env python3
"""
Tracker.gg Real-Time Data Collection for SMITE 2 Divine Arsenal
Implements Grok's recommendations for API-driven data collection
"""

import logging
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MatchData:
    """Real-time match data from Tracker.gg."""
    match_id: str
    player_name: str
    god_name: str
    role: str
    team_players: List[Dict[str, Any]]
    enemy_players: List[Dict[str, Any]]
    detected_items: Dict[str, List[str]]
    match_duration: int
    game_mode: str
    timestamp: datetime


@dataclass
class EnemyItemData:
    """Enemy item data for real-time analysis."""
    player_name: str
    god_name: str
    items: List[str]
    last_updated: datetime
    confidence: float  # How confident we are in the data


class TrackerRealtimeCollector:
    """
    Real-time data collector for Tracker.gg integration.
    
    Implements Grok's recommendations:
    - API-driven data collection (no screen scraping)
    - Respect rate limits
    - Cache data to reduce API calls
    - TOS-compliant data collection
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://public-api.tracker.gg/v2/smite2"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SMITE2-Divine-Arsenal/1.0 (Educational Tool)",
            "Accept": "application/json"
        })
        
        # Rate limiting
        self.rate_limit = 60  # requests per minute
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_reset = datetime.now() + timedelta(minutes=1)
        
        # Caching
        self.match_cache = {}
        self.player_cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Data collection settings
        self.polling_interval = 60  # seconds
        self.max_retries = 3
        
    def _respect_rate_limit(self):
        """Respect Tracker.gg rate limits."""
        now = datetime.now()
        
        # Reset counter if minute has passed
        if now > self.rate_limit_reset:
            self.request_count = 0
            self.rate_limit_reset = now + timedelta(minutes=1)
        
        # Check if we're at the limit
        if self.request_count >= self.rate_limit:
            sleep_time = (self.rate_limit_reset - now).total_seconds()
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                self.request_count = 0
                self.rate_limit_reset = datetime.now() + timedelta(minutes=1)
        
        # Ensure minimum time between requests
        time_since_last = time.time() - self.last_request_time
        if time_since_last < 1.0:  # Minimum 1 second between requests
            time.sleep(1.0 - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _make_api_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make a rate-limited API request to Tracker.gg."""
        try:
            self._respect_rate_limit()
            
            url = f"{self.base_url}/{endpoint}"
            if self.api_key:
                params = params or {}
                params["api_key"] = self.api_key
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded, backing off")
                time.sleep(60)  # Back off for 1 minute
                return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
    
    def get_player_current_match(self, player_name: str) -> Optional[MatchData]:
        """
        Get current match data for a player.
        
        Args:
            player_name: Player name to look up
            
        Returns:
            MatchData if player is in a match, None otherwise
        """
        try:
            # Check cache first
            cache_key = f"match_{player_name}"
            if cache_key in self.match_cache:
                cached = self.match_cache[cache_key]
                if datetime.now() - cached.timestamp < timedelta(seconds=self.cache_duration):
                    return cached
            
            # Get player profile
            profile_data = self._make_api_request(f"profile/{player_name}")
            if not profile_data:
                return None
            
            # Check if player is currently in a match
            current_match = profile_data.get("data", {}).get("currentMatch")
            if not current_match:
                return None
            
            # Extract match data
            match_id = current_match.get("matchId")
            god_name = current_match.get("godName")
            role = current_match.get("role")
            match_duration = current_match.get("matchDuration", 0)
            game_mode = current_match.get("gameMode", "conquest")
            
            # Get team and enemy players
            team_players = current_match.get("teamPlayers", [])
            enemy_players = current_match.get("enemyPlayers", [])
            
            # Extract detected items (if available)
            detected_items = {}
            for player in team_players + enemy_players:
                player_name = player.get("playerName")
                items = player.get("items", [])
                if player_name and items:
                    detected_items[player_name] = items
            
            # Create match data
            match_data = MatchData(
                match_id=match_id,
                player_name=player_name,
                god_name=god_name,
                role=role,
                team_players=team_players,
                enemy_players=enemy_players,
                detected_items=detected_items,
                match_duration=match_duration,
                game_mode=game_mode,
                timestamp=datetime.now()
            )
            
            # Cache the result
            self.match_cache[cache_key] = match_data
            
            logger.info(f"Retrieved current match for {player_name}: {god_name} ({role})")
            return match_data
            
        except Exception as e:
            logger.error(f"Error getting current match for {player_name}: {e}")
            return None
    
    def get_enemy_items_real_time(self, match_data: MatchData) -> Dict[str, EnemyItemData]:
        """
        Get real-time enemy item data from match.
        
        Args:
            match_data: Current match data
            
        Returns:
            Dict of enemy player names to their item data
        """
        enemy_items = {}
        
        try:
            for enemy_player in match_data.enemy_players:
                player_name = enemy_player.get("playerName")
                god_name = enemy_player.get("godName")
                items = enemy_player.get("items", [])
                
                if player_name and god_name:
                    # Calculate confidence based on data quality
                    confidence = 0.5  # Base confidence
                    
                    # Higher confidence if we have items
                    if items:
                        confidence += 0.3
                    
                    # Higher confidence if we have recent data
                    time_diff = datetime.now() - match_data.timestamp
                    if time_diff.total_seconds() < 60:  # Less than 1 minute old
                        confidence += 0.2
                    
                    enemy_items[player_name] = EnemyItemData(
                        player_name=player_name,
                        god_name=god_name,
                        items=items,
                        last_updated=match_data.timestamp,
                        confidence=min(confidence, 1.0)
                    )
            
            logger.info(f"Extracted enemy items for {len(enemy_items)} players")
            return enemy_items
            
        except Exception as e:
            logger.error(f"Error extracting enemy items: {e}")
            return {}
    
    def get_player_recent_matches(self, player_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent matches for a player.
        
        Args:
            player_name: Player name
            limit: Number of recent matches to retrieve
            
        Returns:
            List of recent match data
        """
        try:
            # Check cache first
            cache_key = f"recent_{player_name}_{limit}"
            if cache_key in self.player_cache:
                cached = self.player_cache[cache_key]
                if datetime.now() - cached["timestamp"] < timedelta(seconds=self.cache_duration):
                    return cached["matches"]
            
            # Get recent matches
            matches_data = self._make_api_request(f"profile/{player_name}/matches", {
                "limit": limit
            })
            
            if not matches_data:
                return []
            
            matches = matches_data.get("data", {}).get("matches", [])
            
            # Cache the result
            self.player_cache[cache_key] = {
                "matches": matches,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Retrieved {len(matches)} recent matches for {player_name}")
            return matches
            
        except Exception as e:
            logger.error(f"Error getting recent matches for {player_name}: {e}")
            return []
    
    def analyze_match_meta(self, match_data: MatchData) -> Dict[str, Any]:
        """
        Analyze match meta data for build optimization.
        
        Args:
            match_data: Current match data
            
        Returns:
            Meta analysis results
        """
        try:
            analysis = {
                "team_composition": {
                    "gods": [p.get("godName") for p in match_data.team_players if p.get("godName")],
                    "roles": [p.get("role") for p in match_data.team_players if p.get("role")]
                },
                "enemy_composition": {
                    "gods": [p.get("godName") for p in match_data.enemy_players if p.get("godName")],
                    "roles": [p.get("role") for p in match_data.enemy_players if p.get("role")]
                },
                "detected_items": match_data.detected_items,
                "match_phase": self._determine_match_phase(match_data.match_duration),
                "game_mode": match_data.game_mode,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # Add composition analysis
            analysis["enemy_composition"]["type"] = self._analyze_composition_type(
                analysis["enemy_composition"]["gods"]
            )
            
            logger.info(f"Analyzed match meta: {analysis['enemy_composition']['type']}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing match meta: {e}")
            return {}
    
    def _determine_match_phase(self, duration_seconds: int) -> str:
        """Determine match phase based on duration."""
        if duration_seconds < 300:  # Less than 5 minutes
            return "early_game"
        elif duration_seconds < 900:  # Less than 15 minutes
            return "mid_game"
        else:
            return "late_game"
    
    def _analyze_composition_type(self, gods: List[str]) -> str:
        """Analyze enemy composition type."""
        if not gods:
            return "unknown"
        
        # Count damage types
        physical_count = 0
        magical_count = 0
        healing_count = 0
        
        for god in gods:
            god_lower = god.lower()
            
            # Check for healing gods
            if any(healer in god_lower for healer in ["aphrodite", "hel", "ra", "chang'e"]):
                healing_count += 1
            
            # This is simplified - in a real implementation, you'd have a god database
            # For now, we'll use a basic heuristic
            if any(physical in god_lower for physical in ["hunter", "warrior", "assassin"]):
                physical_count += 1
            else:
                magical_count += 1
        
        # Determine composition type
        if healing_count >= 2:
            return "healing_comp"
        elif physical_count >= 3:
            return "heavy_physical"
        elif magical_count >= 3:
            return "heavy_magical"
        else:
            return "balanced"
    
    def start_realtime_monitoring(self, player_name: str, callback=None):
        """
        Start real-time monitoring for a player.
        
        Args:
            player_name: Player to monitor
            callback: Function to call with match updates
        """
        logger.info(f"Starting real-time monitoring for {player_name}")
        
        try:
            while True:
                # Get current match data
                match_data = self.get_player_current_match(player_name)
                
                if match_data and callback:
                    # Analyze the match
                    meta_analysis = self.analyze_match_meta(match_data)
                    enemy_items = self.get_enemy_items_real_time(match_data)
                    
                    # Call the callback with updates
                    callback({
                        "match_data": match_data,
                        "meta_analysis": meta_analysis,
                        "enemy_items": enemy_items,
                        "timestamp": datetime.now()
                    })
                
                # Wait before next poll
                time.sleep(self.polling_interval)
                
        except KeyboardInterrupt:
            logger.info(f"Stopped monitoring for {player_name}")
        except Exception as e:
            logger.error(f"Error in real-time monitoring: {e}")
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API status and rate limit information."""
        return {
            "api_key_configured": bool(self.api_key),
            "rate_limit": self.rate_limit,
            "current_requests": self.request_count,
            "rate_limit_reset": self.rate_limit_reset.isoformat(),
            "polling_interval": self.polling_interval,
            "cache_duration": self.cache_duration,
            "status": "operational"
        } 