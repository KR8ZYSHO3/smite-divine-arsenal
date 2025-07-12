#!/usr/bin/env python3
"""
Fantasy League System for SMITE 2 Divine Arsenal
Integrates with Tracker.gg API for pro player stats
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Blueprint, request, jsonify
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask Blueprint
fantasy_bp = Blueprint('fantasy', __name__, url_prefix='/api/fantasy')

# Database Models (add these to your existing models)
Base = declarative_base()

class FantasyLeague(Base):
    __tablename__ = 'fantasy_leagues'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    max_teams = Column(Integer, default=8)
    scoring_rules = Column(JSON, default={
        'win': 20,
        'kill': 2,
        'death': -1,
        'assist': 1,
        'ward_placed': 0.5,
        'structure_damage': 0.001  # per 1000 damage
    })
    
    teams = relationship("FantasyTeam", back_populates="league")

class FantasyTeam(Base):
    __tablename__ = 'fantasy_teams'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Link to user system
    league_id = Column(Integer, ForeignKey('fantasy_leagues.id'), nullable=False)
    team_name = Column(String(50), nullable=False)
    drafted_players = Column(JSON, default={})  # {"solo": "pro_id", "jungle": "pro_id", ...}
    total_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    league = relationship("FantasyLeague", back_populates="teams")

class FantasyScore(Base):
    __tablename__ = 'fantasy_scores'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('fantasy_teams.id'), nullable=False)
    player_id = Column(String(50), nullable=False)  # Tracker.gg player ID
    match_date = Column(DateTime, nullable=False)
    stats = Column(JSON, default={})  # Raw stats from API
    points = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

# Tracker.gg API Integration
class TrackerGGAPI:
    """Handles communication with Tracker.gg API for SMITE 2 pro stats."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tracker.gg/api/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "SMITE2-Divine-Arsenal/1.0"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_player_stats(self, player_id: str, days: int = 7) -> Optional[Dict[str, Any]]:
        """Fetch player stats from Tracker.gg API."""
        try:
            url = f"{self.base_url}/smite2/standard/profile/{player_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._extract_relevant_stats(data)
            elif response.status_code == 429:
                logger.warning(f"Rate limit hit for player {player_id}")
                return None
            else:
                logger.error(f"API error for player {player_id}: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request failed for player {player_id}: {e}")
            return None
    
    def _extract_relevant_stats(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant stats for fantasy scoring."""
        try:
            segments = api_data.get('data', {}).get('segments', [])
            
            # Find the overview segment
            overview = None
            for segment in segments:
                if segment.get('type') == 'overview':
                    overview = segment
                    break
            
            if not overview:
                return {}
            
            stats = overview.get('stats', {})
            
            return {
                'wins': stats.get('wins', {}).get('value', 0),
                'losses': stats.get('losses', {}).get('value', 0),
                'kills': stats.get('kills', {}).get('value', 0),
                'deaths': stats.get('deaths', {}).get('value', 0),
                'assists': stats.get('assists', {}).get('value', 0),
                'kda': stats.get('kda', {}).get('value', 0),
                'wards_placed': stats.get('wardsPlaced', {}).get('value', 0),
                'structure_damage': stats.get('structureDamage', {}).get('value', 0),
                'matches_played': stats.get('matchesPlayed', {}).get('value', 0)
            }
            
        except Exception as e:
            logger.error(f"Error extracting stats: {e}")
            return {}

# Fantasy Scoring Engine
class FantasyScorer:
    """Handles scoring calculations for fantasy teams."""
    
    def __init__(self, tracker_api: TrackerGGAPI):
        self.tracker_api = tracker_api
    
    def calculate_player_score(self, stats: Dict[str, Any], scoring_rules: Dict[str, float]) -> float:
        """Calculate fantasy points for a player based on stats and scoring rules."""
        score = 0.0
        
        # Basic scoring
        score += stats.get('wins', 0) * scoring_rules.get('win', 20)
        score += stats.get('kills', 0) * scoring_rules.get('kill', 2)
        score += stats.get('deaths', 0) * scoring_rules.get('death', -1)
        score += stats.get('assists', 0) * scoring_rules.get('assist', 1)
        score += stats.get('wards_placed', 0) * scoring_rules.get('ward_placed', 0.5)
        score += (stats.get('structure_damage', 0) / 1000) * scoring_rules.get('structure_damage', 0.001)
        
        # Bonus for high KDA
        kda = stats.get('kda', 0)
        if kda >= 3.0:
            score += 10  # Bonus for exceptional performance
        elif kda >= 2.0:
            score += 5   # Bonus for good performance
        
        return round(score, 2)
    
    def score_team(self, team: FantasyTeam, days: int = 7) -> float:
        """Score an entire fantasy team based on recent performance."""
        total_score = 0.0
        
        drafted_players = team.drafted_players or {}
        for role, player_id in drafted_players.items():
            if not player_id:
                continue
                
            # Get player stats
            stats = self.tracker_api.get_player_stats(player_id, days)
            if not stats:
                continue
            
            # Calculate score
            scoring_rules = team.league.scoring_rules if team.league else {}
            player_score = self.calculate_player_score(stats, scoring_rules)
            total_score += player_score
            
            # Store individual score record
            score_record = FantasyScore(
                team_id=team.id,
                player_id=player_id,
                match_date=datetime.utcnow(),
                stats=stats,
                points=player_score
            )
            # Note: You'd add this to your database session
            
        return round(total_score, 2)

# Flask Routes
@fantasy_bp.route('/leagues', methods=['GET'])
def get_leagues():
    """Get all fantasy leagues."""
    # Implementation would fetch from database
    return jsonify({
        'leagues': [
            {
                'id': 1,
                'name': 'SPL 2025 Fantasy',
                'start_date': '2025-01-15',
                'end_date': '2025-04-15',
                'teams_count': 6,
                'max_teams': 8
            }
        ]
    })

@fantasy_bp.route('/draft-team', methods=['POST'])
def draft_team():
    """Draft a fantasy team."""
    data = request.json
    
    # Validate draft
    required_roles = ['solo', 'jungle', 'mid', 'carry', 'support']
    team = data.get('team', {})
    
    if not all(role in team for role in required_roles):
        return jsonify({'error': 'Must draft all 5 roles'}), 400
    
    if len(set(team.values())) != 5:
        return jsonify({'error': 'Cannot draft same player twice'}), 400
    
    # Here you would save to database
    return jsonify({
        'message': 'Team drafted successfully',
        'team': team,
        'team_id': 'generated_id'
    })

@fantasy_bp.route('/leaderboard/<int:league_id>', methods=['GET'])
def get_leaderboard(league_id: int):
    """Get fantasy league leaderboard."""
    # Mock data - replace with database query
    return jsonify({
        'leaderboard': [
            {'rank': 1, 'team_name': 'Divine Drafters', 'score': 245.5, 'user': 'player1'},
            {'rank': 2, 'team_name': 'Arena Legends', 'score': 232.0, 'user': 'player2'},
            {'rank': 3, 'team_name': 'Conquest Kings', 'score': 218.5, 'user': 'player3'}
        ]
    })

@fantasy_bp.route('/score-update', methods=['POST'])
def manual_score_update():
    """Manually trigger score update (for testing)."""
    api_key = os.getenv('TRACKER_GG_API_KEY')
    if not api_key:
        return jsonify({'error': 'API key not configured'}), 500
    
    try:
        tracker_api = TrackerGGAPI(api_key)
        scorer = FantasyScorer(tracker_api)
        
        # Here you would update all teams
        # For now, return success
        return jsonify({
            'message': 'Scores updated successfully',
            'updated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Score update failed: {e}")
        return jsonify({'error': 'Score update failed'}), 500

# Cron Job Function (for Render Cron)
def daily_score_update():
    """Daily cron job to update fantasy scores."""
    api_key = os.getenv('TRACKER_GG_API_KEY')
    if not api_key:
        logger.error("No Tracker.gg API key configured")
        return
    
    try:
        tracker_api = TrackerGGAPI(api_key)
        scorer = FantasyScorer(tracker_api)
        
        # Get all active leagues
        # active_leagues = FantasyLeague.query.filter(
        #     FantasyLeague.start_date <= datetime.utcnow(),
        #     FantasyLeague.end_date >= datetime.utcnow()
        # ).all()
        
        # For each league, update team scores
        # This would be implemented with your database session
        
        logger.info("Daily score update completed successfully")
        
    except Exception as e:
        logger.error(f"Daily score update failed: {e}")

if __name__ == "__main__":
    # Test the API integration
    api_key = os.getenv('TRACKER_GG_API_KEY')
    if api_key:
        tracker = TrackerGGAPI(api_key)
        # Test with a known player ID
        stats = tracker.get_player_stats('test_player_id')
        print(f"Test stats: {stats}")
    else:
        print("Set TRACKER_GG_API_KEY environment variable to test") 