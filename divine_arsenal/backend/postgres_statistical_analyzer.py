#!/usr/bin/env python3
"""
PostgreSQL Statistical Analyzer for SMITE 2 Divine Arsenal
Migration from SQLite to PostgreSQL using the unified database adapter
"""

import json
import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sqlalchemy import text

from postgres_database_adapter import PostgreSQLDatabaseAdapter

logger = logging.getLogger(__name__)


@dataclass
class MatchData:
    """Represents match performance data."""
    match_id: str
    god_name: str
    role: str
    items: List[str]
    win: bool
    kills: int
    deaths: int
    assists: int
    damage_dealt: int
    damage_mitigated: int
    healing: int
    match_duration: int
    enemy_comp: List[str]
    patch_version: str
    game_mode: str = "Conquest"
    player_skill: str = "Average"


@dataclass
class ItemSynergy:
    """Statistical item synergy data."""
    item1: str
    item2: str
    synergy_score: float
    win_rate_boost: float
    matches_analyzed: int
    confidence_level: float
    patch_relevant: str


@dataclass
class GodPerformance:
    """God statistical performance data."""
    god_name: str
    role: str
    win_rate: float
    avg_kda: float
    avg_damage: float
    avg_mitigated: float
    pick_rate: float
    ban_rate: float
    matches_analyzed: int
    patch_version: str
    meta_tier: str  # S+, S, A, B, C


@dataclass
class MetaTrend:
    """Meta trend analysis."""
    trend_type: str  # "item_popularity", "god_tier", "role_shift"
    description: str
    impact_score: float  # 0-100
    patch_introduced: str
    affected_entities: List[str]
    recommendation: str


class PostgreSQLStatisticalAnalyzer:
    """
    PostgreSQL-based statistical analyzer for SMITE 2 Divine Arsenal.
    Replaces the SQLite-based statistical analyzer with PostgreSQL compatibility.
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize with PostgreSQL database adapter."""
        # Use PostgreSQL adapter instead of SQLite
        self.db_adapter = PostgreSQLDatabaseAdapter(db_path)
        self.match_data = []
        self.item_synergies = []
        self.god_performance = []
        self.meta_trends = []
        
        # Statistical configuration
        self.confidence_threshold = 0.7
        self.min_matches_threshold = 50
        self.meta_tiers = ["S+", "S", "A", "B", "C"]
        
        self._init_statistical_tables()

    def _init_statistical_tables(self):
        """Initialize PostgreSQL tables for statistical data."""
        with self.db_adapter.get_connection() as session:
            try:
                # Create statistical tables if they don't exist
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS match_performance (
                        match_id TEXT PRIMARY KEY,
                        god_name TEXT,
                        role TEXT,
                        items TEXT,  -- JSON array
                        win INTEGER,
                        kills INTEGER,
                        deaths INTEGER,
                        assists INTEGER,
                        damage_dealt INTEGER,
                        damage_mitigated INTEGER,
                        healing INTEGER,
                        match_duration INTEGER,
                        enemy_comp TEXT,  -- JSON array
                        patch_version TEXT,
                        game_mode TEXT,
                        player_skill TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS item_synergies (
                        item1 TEXT,
                        item2 TEXT,
                        synergy_score REAL,
                        win_rate_boost REAL,
                        matches_analyzed INTEGER,
                        confidence_level REAL,
                        patch_version TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (item1, item2, patch_version)
                    )
                """))

                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS god_stats (
                        god_name TEXT,
                        role TEXT,
                        patch_version TEXT,
                        win_rate REAL,
                        avg_kda REAL,
                        avg_damage REAL,
                        avg_mitigated REAL,
                        pick_rate REAL,
                        ban_rate REAL,
                        matches_analyzed INTEGER,
                        meta_tier TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (god_name, role, patch_version)
                    )
                """))

                session.commit()
                logger.info("✅ PostgreSQL statistical tables initialized")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error initializing statistical tables: {e}")

    def analyze_patch_trends(self, patch_notes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patch notes for meta trends."""
        trends = []

        if "item_changes" in patch_notes:
            for item, changes in patch_notes["item_changes"].items():
                impact = self._calculate_impact_score(changes)
                if impact > 50:
                    trends.append({
                        "type": "item_shift",
                        "item": item,
                        "impact": impact,
                        "recommendation": f"Monitor {item} performance"
                    })

        return trends

    def _calculate_impact_score(self, changes: Dict[str, Any]) -> float:
        """Calculate impact score for changes."""
        score = 0
        if "damage" in changes:
            score += abs(changes["damage"].get("change_percent", 0)) * 2
        if "cost" in changes:
            score += abs(changes["cost"].get("change_percent", 0)) * 1.5
        return min(score, 100)

    def collect_patch_data(self, patch_notes: Dict[str, Any]) -> List[MetaTrend]:
        """Analyze patch notes to identify meta trends."""
        trends = []

        # Analyze item changes
        if "item_changes" in patch_notes:
            for item, changes in patch_notes["item_changes"].items():
                impact_score = self._calculate_change_impact(changes)

                if impact_score > 70:
                    trend_type = "major_item_shift"
                    description = f"{item} received significant changes - expect meta impact"
                elif impact_score > 40:
                    trend_type = "moderate_item_change"
                    description = f"{item} adjustments may affect build priorities"

                trends.append(MetaTrend(
                    trend_type=trend_type,
                    description=description,
                    impact_score=impact_score,
                    patch_introduced=patch_notes.get("version", "Unknown"),
                    affected_entities=[item],
                    recommendation=self._generate_item_recommendation(item, changes)
                ))

        # Analyze god changes
        if "god_changes" in patch_notes:
            for god, changes in patch_notes["god_changes"].items():
                impact_score = self._calculate_change_impact(changes)

                if impact_score > 60:
                    trends.append(MetaTrend(
                        trend_type="god_tier_shift",
                        description=f"{god} tier changes detected",
                        impact_score=impact_score,
                        patch_introduced=patch_notes.get("version", "Unknown"),
                        affected_entities=[god],
                        recommendation=self._generate_god_recommendation(god, changes)
                    ))

        self.meta_trends.extend(trends)
        return trends

    def analyze_item_synergies(self, min_matches: int = 100) -> List[ItemSynergy]:
        """Perform correlation analysis to identify item synergies."""
        synergies = []

        # Load match data from PostgreSQL
        with self.db_adapter.get_connection() as session:
            try:
                result = session.execute(text("""
                    SELECT * FROM match_performance 
                    WHERE patch_version = (
                        SELECT patch_version FROM match_performance 
                        GROUP BY patch_version 
                        ORDER BY COUNT(*) DESC 
                        LIMIT 1
                    )
                """))
                
                match_data = []
                for row in result:
                    row_dict = dict(row._mapping)
                    match_data.append(MatchData(
                        match_id=row_dict['match_id'],
                        god_name=row_dict['god_name'],
                        role=row_dict['role'],
                        items=json.loads(row_dict['items']) if row_dict['items'] else [],
                        win=bool(row_dict['win']),
                        kills=row_dict['kills'],
                        deaths=row_dict['deaths'],
                        assists=row_dict['assists'],
                        damage_dealt=row_dict['damage_dealt'],
                        damage_mitigated=row_dict['damage_mitigated'],
                        healing=row_dict['healing'],
                        match_duration=row_dict['match_duration'],
                        enemy_comp=json.loads(row_dict['enemy_comp']) if row_dict['enemy_comp'] else [],
                        patch_version=row_dict['patch_version'],
                        game_mode=row_dict['game_mode'],
                        player_skill=row_dict['player_skill']
                    ))

            except Exception as e:
                logger.error(f"Error loading match data: {e}")
                return []

        # Group matches by item combinations
        item_combinations = defaultdict(list)

        for match in match_data:
            items = match.items
            # Generate all pairs of items
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    pair = tuple(sorted([items[i], items[j]]))
                    item_combinations[pair].append(match)

        # Analyze each combination
        for (item1, item2), matches in item_combinations.items():
            if len(matches) < min_matches:
                continue

            # Calculate synergy metrics
            win_rate = sum(1 for m in matches if m.win) / len(matches)

            # Compare to individual item win rates
            item1_matches = [m for m in match_data if item1 in m.items]
            item2_matches = [m for m in match_data if item2 in m.items]

            item1_wr = (sum(1 for m in item1_matches if m.win) / len(item1_matches)
                       if item1_matches else 0.5)
            item2_wr = (sum(1 for m in item2_matches if m.win) / len(item2_matches)
                       if item2_matches else 0.5)

            # Calculate synergy score
            expected_wr = (item1_wr + item2_wr) / 2
            synergy_boost = win_rate - expected_wr
            synergy_score = min(100, max(0, synergy_boost * 200))

            # Calculate confidence level
            confidence = min(1.0, len(matches) / 200)

            synergies.append(ItemSynergy(
                item1=item1,
                item2=item2,
                synergy_score=synergy_score,
                win_rate_boost=synergy_boost,
                matches_analyzed=len(matches),
                confidence_level=confidence,
                patch_relevant=matches[0].patch_version if matches else "Unknown"
            ))

        # Store synergies in PostgreSQL
        self._store_synergies(synergies)
        return synergies

    def predict_build_success(self, god: str, role: str, items: List[str], 
                            enemy_comp: List[str], patch: str = "OB12") -> Dict[str, float]:
        """Predict build success using statistical analysis."""
        try:
            # Load historical data for this god/role combination
            with self.db_adapter.get_connection() as session:
                result = session.execute(text("""
                    SELECT * FROM match_performance 
                    WHERE god_name = :god AND role = :role AND patch_version = :patch
                    LIMIT 1000
                """), {"god": god, "role": role, "patch": patch})

                matches = []
                for row in result:
                    row_dict = dict(row._mapping)
                    matches.append(MatchData(
                        match_id=row_dict['match_id'],
                        god_name=row_dict['god_name'],
                        role=row_dict['role'],
                        items=json.loads(row_dict['items']) if row_dict['items'] else [],
                        win=bool(row_dict['win']),
                        kills=row_dict['kills'],
                        deaths=row_dict['deaths'],
                        assists=row_dict['assists'],
                        damage_dealt=row_dict['damage_dealt'],
                        damage_mitigated=row_dict['damage_mitigated'],
                        healing=row_dict['healing'],
                        match_duration=row_dict['match_duration'],
                        enemy_comp=json.loads(row_dict['enemy_comp']) if row_dict['enemy_comp'] else [],
                        patch_version=row_dict['patch_version'],
                        game_mode=row_dict['game_mode'],
                        player_skill=row_dict['player_skill']
                    ))

            if not matches:
                return self._heuristic_prediction(god, role, items, enemy_comp, patch)

            # Calculate statistics
            similar_builds = [m for m in matches if len(set(m.items) & set(items)) >= 3]
            
            if similar_builds:
                win_rate = sum(1 for m in similar_builds if m.win) / len(similar_builds)
                avg_kda = statistics.mean(
                    (m.kills + m.assists) / max(1, m.deaths) for m in similar_builds
                )
                avg_damage = statistics.mean(m.damage_dealt for m in similar_builds)
            else:
                return self._heuristic_prediction(god, role, items, enemy_comp, patch)

            return {
                "win_rate": win_rate,
                "predicted_kda": avg_kda,
                "predicted_damage": avg_damage,
                "confidence": min(1.0, len(similar_builds) / 50),
                "matches_analyzed": len(similar_builds)
            }

        except Exception as e:
            logger.error(f"Error predicting build success: {e}")
            return self._heuristic_prediction(god, role, items, enemy_comp, patch)

    def _heuristic_prediction(self, god: str, role: str, items: List[str], 
                            enemy_comp: List[str], patch: str) -> Dict[str, float]:
        """Fallback heuristic prediction when insufficient data."""
        # Basic heuristic based on role and items
        base_win_rate = 0.5
        
        # Role-based adjustments
        role_adjustments = {
            "Mid": 0.52,
            "Jungle": 0.51,
            "Solo": 0.49,
            "Carry": 0.50,
            "Support": 0.48
        }
        
        win_rate = role_adjustments.get(role, base_win_rate)
        
        return {
            "win_rate": win_rate,
            "predicted_kda": 2.0,
            "predicted_damage": 30000,
            "confidence": 0.3,
            "matches_analyzed": 0
        }

    def _calculate_change_impact(self, changes: Dict[str, Any]) -> float:
        """Calculate impact score for patch changes."""
        score = 0
        for change_type, change_data in changes.items():
            if isinstance(change_data, dict):
                change_percent = change_data.get("change_percent", 0)
                if change_type in ["damage", "power", "protection"]:
                    score += abs(change_percent) * 2
                elif change_type == "cost":
                    score += abs(change_percent) * 1.5
                else:
                    score += abs(change_percent)
        return min(score, 100)

    def _generate_item_recommendation(self, item: str, changes: Dict[str, Any]) -> str:
        """Generate recommendation for item changes."""
        if any(change.get("change_percent", 0) > 0 for change in changes.values() if isinstance(change, dict)):
            return f"Consider prioritizing {item} due to buffs"
        else:
            return f"Consider alternatives to {item} due to nerfs"

    def _generate_god_recommendation(self, god: str, changes: Dict[str, Any]) -> str:
        """Generate recommendation for god changes."""
        if any(change.get("change_percent", 0) > 0 for change in changes.values() if isinstance(change, dict)):
            return f"{god} may rise in tier due to buffs"
        else:
            return f"{god} may fall in tier due to nerfs"

    def _store_synergies(self, synergies: List[ItemSynergy]):
        """Store synergies in PostgreSQL database."""
        with self.db_adapter.get_connection() as session:
            try:
                for synergy in synergies:
                    session.execute(text("""
                        INSERT INTO item_synergies 
                        (item1, item2, synergy_score, win_rate_boost, matches_analyzed, 
                         confidence_level, patch_version)
                        VALUES (:item1, :item2, :synergy_score, :win_rate_boost, 
                               :matches_analyzed, :confidence_level, :patch_version)
                        ON CONFLICT (item1, item2, patch_version) 
                        DO UPDATE SET 
                            synergy_score = EXCLUDED.synergy_score,
                            win_rate_boost = EXCLUDED.win_rate_boost,
                            matches_analyzed = EXCLUDED.matches_analyzed,
                            confidence_level = EXCLUDED.confidence_level,
                            last_updated = CURRENT_TIMESTAMP
                    """), {
                        "item1": synergy.item1,
                        "item2": synergy.item2,
                        "synergy_score": synergy.synergy_score,
                        "win_rate_boost": synergy.win_rate_boost,
                        "matches_analyzed": synergy.matches_analyzed,
                        "confidence_level": synergy.confidence_level,
                        "patch_version": synergy.patch_relevant
                    })
                
                session.commit()
                logger.info(f"✅ Stored {len(synergies)} synergies in PostgreSQL")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error storing synergies: {e}")

    def close(self):
        """Close database connections."""
        if hasattr(self, 'db_adapter'):
            self.db_adapter.close()
        logger.info("✅ PostgreSQL Statistical Analyzer closed")


# For backward compatibility
StatisticalAnalyzer = PostgreSQLStatisticalAnalyzer 