#!/usr/bin/env python3
"""
Player Performance Integration Module for SMITE 2 Build Optimizer
"""

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

import numpy as np


class PlayStyle(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    UTILITY = "utility"


class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class PlayerProfile:
    """Player performance profile."""

    player_id: str
    games_played: int
    avg_win_rate: float
    avg_kda: float
    preferred_playstyle: PlayStyle
    skill_level: SkillLevel
    favorite_gods: List[str]
    item_preferences: Dict[str, float]
    last_updated: datetime


class PlayerPerformanceIntegrator:
    """Integrates player performance with build recommendations."""

    def __init__(self, db_path: str = "player_performance.db"):
        self.db_path = db_path
        self.calibration_games_required = 5
        self.meta_weight = 0.40  # 40% meta data
        self.player_weight = 0.60  # 60% player data
        self._init_database()

    def _init_database(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS player_profiles (
                player_id TEXT PRIMARY KEY,
                profile_data TEXT,
                calibration_status TEXT,
                games_analyzed INTEGER,
                last_updated DATETIME
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS player_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT,
                match_data TEXT,
                performance_score REAL,
                timestamp DATETIME
            )
        """
        )

        conn.commit()
        conn.close()

    def start_calibration(self, player_id: str) -> Dict[str, Any]:
        """Start player calibration process."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if player exists
        cursor.execute("SELECT * FROM player_profiles WHERE player_id = ?", (player_id,))
        if cursor.fetchone():
            conn.close()
            return {"status": "existing_player", "calibration_needed": False}

        # Create new player
        initial_profile = PlayerProfile(
            player_id=player_id,
            games_played=0,
            avg_win_rate=0.5,
            avg_kda=1.0,
            preferred_playstyle=PlayStyle.BALANCED,
            skill_level=SkillLevel.INTERMEDIATE,
            favorite_gods=[],
            item_preferences={},
            last_updated=datetime.now(),
        )

        profile_dict = asdict(initial_profile)
        # Convert enums to strings for JSON serialization
        profile_dict["preferred_playstyle"] = profile_dict["preferred_playstyle"].value
        profile_dict["skill_level"] = profile_dict["skill_level"].value
        profile_dict["last_updated"] = profile_dict["last_updated"].isoformat()

        cursor.execute(
            """
            INSERT INTO player_profiles 
            (player_id, profile_data, calibration_status, games_analyzed, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """,
            (player_id, json.dumps(profile_dict), "calibrating", 0, datetime.now()),
        )

        conn.commit()
        conn.close()

        return {
            "status": "calibration_started",
            "games_needed": self.calibration_games_required,
            "instructions": [
                "Play 5 games with your preferred gods",
                "Use different item builds",
                "Play your normal style",
            ],
        }

    def add_calibration_match(self, player_id: str, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a calibration match."""

        performance_score = self._calculate_performance_score(match_data)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO player_matches 
            (player_id, match_data, performance_score, timestamp)
            VALUES (?, ?, ?, ?)
        """,
            (player_id, json.dumps(match_data), performance_score, datetime.now()),
        )

        # Check progress
        cursor.execute("SELECT COUNT(*) FROM player_matches WHERE player_id = ?", (player_id,))
        games_analyzed = cursor.fetchone()[0]

        cursor.execute(
            """
            UPDATE player_profiles 
            SET games_analyzed = ?, last_updated = ?
            WHERE player_id = ?
        """,
            (games_analyzed, datetime.now(), player_id),
        )

        conn.commit()
        conn.close()

        if games_analyzed >= self.calibration_games_required:
            return self._complete_calibration(player_id)

        return {
            "status": "calibration_in_progress",
            "games_analyzed": games_analyzed,
            "games_remaining": self.calibration_games_required - games_analyzed,
        }

    def _calculate_performance_score(self, match_data: Dict[str, Any]) -> float:
        """Calculate 0-100 performance score."""

        base_score = 60.0 if match_data.get("win", False) else 30.0

        kills = match_data.get("kills", 0)
        deaths = max(match_data.get("deaths", 1), 1)
        assists = match_data.get("assists", 0)
        kda = (kills + assists) / deaths
        kda_score = min(25.0, kda * 8)

        damage = match_data.get("damage_dealt", 0)
        damage_score = min(15.0, damage / 2000)

        return min(100.0, base_score + kda_score + damage_score)

    def _complete_calibration(self, player_id: str) -> Dict[str, Any]:
        """Complete calibration and build profile."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT match_data, performance_score FROM player_matches 
            WHERE player_id = ? ORDER BY timestamp DESC LIMIT 10
        """,
            (player_id,),
        )

        matches = cursor.fetchall()

        # Analyze matches
        match_data_list = [json.loads(match[0]) for match in matches]
        performance_scores = [match[1] for match in matches]

        avg_performance = np.mean(performance_scores)

        # Determine skill level
        if avg_performance >= 80:
            skill_level = SkillLevel.EXPERT
        elif avg_performance >= 65:
            skill_level = SkillLevel.ADVANCED
        elif avg_performance >= 45:
            skill_level = SkillLevel.INTERMEDIATE
        else:
            skill_level = SkillLevel.BEGINNER

        # Analyze playstyle
        aggression_score = 0
        defensive_score = 0

        for match in match_data_list:
            kills = match.get("kills", 0)
            deaths = match.get("deaths", 1)
            damage_mitigated = match.get("damage_mitigated", 0)

            if kills > deaths:
                aggression_score += 1
            if damage_mitigated > 15000:
                defensive_score += 1

        if aggression_score > defensive_score:
            playstyle = PlayStyle.AGGRESSIVE
        elif defensive_score > aggression_score:
            playstyle = PlayStyle.DEFENSIVE
        else:
            playstyle = PlayStyle.BALANCED

        # Get favorite gods
        god_counts: Dict[str, int] = {}
        for match in match_data_list:
            god = match.get("god_name", "Unknown")
            god_counts[god] = god_counts.get(god, 0) + 1

        favorite_gods = sorted(god_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        # Build updated profile
        updated_profile = PlayerProfile(
            player_id=player_id,
            games_played=len(matches),
            avg_win_rate=float(avg_performance / 100),
            avg_kda=float(avg_performance / 25),
            preferred_playstyle=playstyle,
            skill_level=skill_level,
            favorite_gods=[god for god, _ in favorite_gods],
            item_preferences={},
            last_updated=datetime.now(),
        )

        profile_dict = asdict(updated_profile)
        # Convert enums to strings for JSON serialization
        profile_dict["preferred_playstyle"] = profile_dict["preferred_playstyle"].value
        profile_dict["skill_level"] = profile_dict["skill_level"].value
        profile_dict["last_updated"] = profile_dict["last_updated"].isoformat()

        cursor.execute(
            """
            UPDATE player_profiles 
            SET profile_data = ?, calibration_status = ?, last_updated = ?
            WHERE player_id = ?
        """,
            (json.dumps(profile_dict), "completed", datetime.now(), player_id),
        )

        conn.commit()
        conn.close()

        return {
            "status": "calibration_completed",
            "player_profile": profile_dict,
            "personalization_ready": True,
        }

    def get_personalized_weights(self, player_id: str) -> Dict[str, float]:
        """Get personalized build weights for a player."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT profile_data FROM player_profiles WHERE player_id = ?", (player_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return {
                "meta_weight": 0.6,
                "player_weight": 0.4,
                "aggression_modifier": 1.0,
                "defensive_modifier": 1.0,
            }

        profile_data = json.loads(result[0])

        weights = {
            "meta_weight": self.meta_weight,
            "player_weight": self.player_weight,
            "aggression_modifier": 1.0,
            "defensive_modifier": 1.0,
        }

        # Adjust based on playstyle
        playstyle = profile_data.get("preferred_playstyle", "balanced")
        if playstyle == "aggressive":
            weights["aggression_modifier"] = 1.3
            weights["defensive_modifier"] = 0.8
        elif playstyle == "defensive":
            weights["aggression_modifier"] = 0.8
            weights["defensive_modifier"] = 1.3

        # Adjust based on skill level
        skill = profile_data.get("skill_level", "intermediate")
        if skill == "expert":
            weights["player_weight"] = 0.7
            weights["meta_weight"] = 0.3
        elif skill == "beginner":
            weights["player_weight"] = 0.3
            weights["meta_weight"] = 0.7

        return weights


# Test function
def test_player_system():
    """Test the player performance system."""

    integrator = PlayerPerformanceIntegrator()
    player_id = "test_player_123"

    # Start calibration
    result = integrator.start_calibration(player_id)
    print("🎯 PLAYER PERFORMANCE INTEGRATION TEST")
    print("=" * 50)
    print(f"Calibration: {result['status']}")

    # Add test matches
    for i in range(6):
        match = {
            "god_name": "Hecate",
            "role": "Mid",
            "win": i % 2 == 0,
            "kills": 8 + i,
            "deaths": 3,
            "assists": 12,
            "damage_dealt": 28000,
            "damage_mitigated": 8000,
        }

        result = integrator.add_calibration_match(player_id, match)
        print(f"Match {i+1}: {result['status']}")

    # Get weights
    weights = integrator.get_personalized_weights(player_id)
    print(f"\nPersonalized Weights:")
    for key, value in weights.items():
        print(f"  {key}: {value:.2f}")

    return integrator


if __name__ == "__main__":
    test_player_system()
