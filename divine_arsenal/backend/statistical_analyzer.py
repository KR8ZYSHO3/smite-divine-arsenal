#!/usr/bin/env python3
"""
Statistical Analysis Module for SMITE 2 Build Optimizer
Analyzes patch data, god/item performance, and meta trends to enhance build recommendations.
"""

import json
import logging
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

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
    player_skill: str = "Average"  # Bronze, Silver, Gold, Platinum, Diamond, Masters, Grandmaster


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


class StatisticalAnalyzer:
    """Advanced statistical analysis for SMITE 2 builds."""

    def __init__(self, db_path: str = "smite_stats.db"):
        self.db_path = db_path
        self.match_data: List[MatchData] = []
        self.god_performance: Dict[str, GodPerformance] = {}
        self.item_synergies: List[ItemSynergy] = []
        self.meta_trends: List[MetaTrend] = []
        self.patch_weights = {
            "OB12": 1.0,  # Current patch
            "OB11": 0.8,  # Recent patch
            "OB10": 0.6,  # Older patch
            "OB9": 0.4,  # Historical
            "OB8": 0.2,  # Legacy data
        }
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for match data storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables for statistical data
        cursor.execute(
            """
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
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS item_synergies (
                item1 TEXT,
                item2 TEXT,
                synergy_score REAL,
                win_rate_boost REAL,
                matches_analyzed INTEGER,
                confidence_level REAL,
                patch_version TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (item1, item2, patch_version)
            )
        """
        )

        cursor.execute(
            """
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
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (god_name, role, patch_version)
            )
        """
        )

        conn.commit()
        conn.close()

    def analyze_patch_trends(self, patch_notes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patch notes for meta trends."""
        trends = []

        # Example implementation
        if "item_changes" in patch_notes:
            for item, changes in patch_notes["item_changes"].items():
                impact = self._calculate_impact_score(changes)
                if impact > 50:
                    trends.append(
                        {
                            "type": "item_shift",
                            "item": item,
                            "impact": impact,
                            "recommendation": f"Monitor {item} performance",
                        }
                    )

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

                trends.append(
                    MetaTrend(
                        trend_type=trend_type,
                        description=description,
                        impact_score=impact_score,
                        patch_introduced=patch_notes.get("version", "Unknown"),
                        affected_entities=[item],
                        recommendation=self._generate_item_recommendation(item, changes),
                    )
                )

        # Analyze god changes
        if "god_changes" in patch_notes:
            for god, changes in patch_notes["god_changes"].items():
                impact_score = self._calculate_change_impact(changes)

                if impact_score > 60:
                    trends.append(
                        MetaTrend(
                            trend_type="god_tier_shift",
                            description=f"{god} tier changes detected",
                            impact_score=impact_score,
                            patch_introduced=patch_notes.get("version", "Unknown"),
                            affected_entities=[god],
                            recommendation=self._generate_god_recommendation(god, changes),
                        )
                    )

        # Analyze system changes (XP, jungle, etc.)
        if "system_changes" in patch_notes:
            for system, changes in patch_notes["system_changes"].items():
                if system == "jungle_xp" and changes.get("buff", 0) > 0:
                    trends.append(
                        MetaTrend(
                            trend_type="role_priority_shift",
                            description="Jungle XP buffs favor aggressive jungle gods",
                            impact_score=75,
                            patch_introduced=patch_notes.get("version", "Unknown"),
                            affected_entities=["Jungle"],
                            recommendation="Prioritize early game jungle gods and jungle-focused items",
                        )
                    )

        self.meta_trends.extend(trends)
        return trends

    def analyze_item_synergies(self, min_matches: int = 100) -> List[ItemSynergy]:
        """Perform correlation analysis to identify item synergies."""
        synergies = []

        # Group matches by item combinations
        item_combinations = defaultdict(list)

        for match in self.match_data:
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
            item1_matches = [m for m in self.match_data if item1 in m.items]
            item2_matches = [m for m in self.match_data if item2 in m.items]

            item1_wr = (
                sum(1 for m in item1_matches if m.win) / len(item1_matches)
                if item1_matches
                else 0.5
            )
            item2_wr = (
                sum(1 for m in item2_matches if m.win) / len(item2_matches)
                if item2_matches
                else 0.5
            )

            expected_wr = (item1_wr + item2_wr) / 2
            win_rate_boost = win_rate - expected_wr

            # Calculate synergy score
            synergy_score = self._calculate_synergy_score(matches, item1, item2)

            # Calculate confidence level
            confidence = min(100, (len(matches) / min_matches) * 100)

            if win_rate_boost > 0.05 and synergy_score > 60:  # Significant synergy
                synergy = ItemSynergy(
                    item1=item1,
                    item2=item2,
                    synergy_score=synergy_score,
                    win_rate_boost=win_rate_boost * 100,
                    matches_analyzed=len(matches),
                    confidence_level=confidence,
                    patch_relevant=self._get_most_relevant_patch(
                        [m.patch_version for m in matches]
                    ),
                )
                synergies.append(synergy)

        self.item_synergies = synergies
        self._store_synergies(synergies)
        return synergies

    def predict_build_success(
        self, god: str, role: str, items: List[str], enemy_comp: List[str], patch: str = "OB12"
    ) -> Dict[str, float]:
        """Use regression models to predict build success probability."""

        # Gather historical data for this god/role combination
        relevant_matches = [m for m in self.match_data if m.god_name == god and m.role == role]

        if len(relevant_matches) < 50:
            # Insufficient data - use heuristic approach
            return self._heuristic_prediction(god, role, items, enemy_comp, patch)

        # Feature extraction
        features = self._extract_build_features(items, enemy_comp, patch)

        # Simple logistic regression prediction
        win_probability = self._logistic_prediction(features, relevant_matches)

        # Performance predictions
        kda_prediction = self._predict_kda(features, relevant_matches)
        damage_prediction = self._predict_damage(features, relevant_matches)

        return {
            "win_probability": win_probability,
            "predicted_kda": kda_prediction,
            "predicted_damage": damage_prediction,
            "confidence": min(100, len(relevant_matches) / 100 * 100),
            "sample_size": len(relevant_matches),
        }

    def generate_meta_recommendations(self, patch: str = "OB12") -> Dict[str, List[str]]:
        """Generate dynamic recommendations based on current meta trends."""
        recommendations: Dict[str, List[str]] = {
            "priority_items": [],
            "avoid_items": [],
            "rising_gods": [],
            "falling_gods": [],
            "role_priorities": [],
            "counter_strategies": [],
        }

        # Analyze current meta trends
        current_trends = [t for t in self.meta_trends if t.patch_introduced == patch]

        for trend in current_trends:
            if trend.trend_type == "major_item_shift" and trend.impact_score > 80:
                recommendations["priority_items"].extend(trend.affected_entities)
            elif trend.trend_type == "god_tier_shift":
                if trend.impact_score > 70:
                    recommendations["rising_gods"].extend(trend.affected_entities)
                elif trend.impact_score < 30:
                    recommendations["falling_gods"].extend(trend.affected_entities)
            elif trend.trend_type == "role_priority_shift":
                recommendations["role_priorities"].append(trend.recommendation)

        # Add item synergy recommendations
        top_synergies = sorted(self.item_synergies, key=lambda x: x.synergy_score, reverse=True)[
            :10
        ]
        for synergy in top_synergies:
            if synergy.patch_relevant == patch:
                recommendations["counter_strategies"].append(
                    f"Strong synergy: {synergy.item1} + {synergy.item2} "
                    f"({synergy.win_rate_boost:.1f}% win rate boost)"
                )

        return recommendations

    def monte_carlo_simulation(
        self,
        god: str,
        role: str,
        build_options: List[List[str]],
        enemy_comps: List[List[str]],
        iterations: int = 1000,
    ) -> Dict[str, Any]:
        """Monte Carlo simulation to test build performance against various scenarios."""
        results = {}

        for build_idx, build in enumerate(build_options):
            build_name = f"Build_{build_idx + 1}"
            wins = 0
            total_kda = 0
            total_damage = 0

            for _ in range(iterations):
                # Randomly select enemy composition
                enemy_comp = enemy_comps[np.random.randint(len(enemy_comps))]

                # Predict outcome
                prediction = self.predict_build_success(god, role, build, enemy_comp)

                # Simulate match outcome
                if np.random.random() < prediction["win_probability"]:
                    wins += 1

                total_kda += prediction["predicted_kda"]
                total_damage += prediction["predicted_damage"]

            results[build_name] = {
                "build": build,
                "win_rate": wins / iterations,
                "avg_kda": total_kda / iterations,
                "avg_damage": total_damage / iterations,
                "consistency_score": self._calculate_consistency(build, enemy_comps),
            }

        # Rank builds by overall score
        for build_name in results:
            score = (
                results[build_name]["win_rate"] * 0.4
                + min(results[build_name]["avg_kda"] / 3.0, 1.0) * 0.3
                + min(results[build_name]["avg_damage"] / 50000, 1.0) * 0.2
                + results[build_name]["consistency_score"] * 0.1
            )
            results[build_name]["overall_score"] = score

        return results

    def cluster_gods_by_playstyle(self) -> Dict[str, List[str]]:
        """Use clustering to group gods by playstyle."""
        clusters: Dict[str, List[str]] = {
            "burst_mages": [],
            "sustain_tanks": [],
            "assassin_junglers": [],
            "utility_supports": [],
            "late_game_carries": [],
            "early_game_bullies": [],
        }

        for god_name, performance in self.god_performance.items():
            # Analyze god characteristics based on performance data
            if performance.avg_damage > 40000 and performance.role == "Mid":
                clusters["burst_mages"].append(god_name)
            elif performance.avg_mitigated > 30000 and performance.role in ["Solo", "Support"]:
                clusters["sustain_tanks"].append(god_name)
            elif performance.avg_kda > 2.5 and performance.role == "Jungle":
                clusters["assassin_junglers"].append(god_name)
            elif performance.role == "Support" and performance.win_rate > 0.52:
                clusters["utility_supports"].append(god_name)
            elif performance.role == "Carry" and performance.avg_damage > 45000:
                clusters["late_game_carries"].append(god_name)

        return clusters

    # Helper methods
    def _calculate_change_impact(self, changes: Dict[str, Any]) -> float:
        """Calculate the impact score of item/god changes."""
        impact: float = 0.0

        if "damage" in changes:
            damage_change = changes["damage"].get("change_percent", 0)
            impact += abs(damage_change) * 2

        if "cooldown" in changes:
            cd_change = changes["cooldown"].get("change_percent", 0)
            impact += abs(cd_change) * 1.5

        if "cost" in changes:
            cost_change = changes["cost"].get("change_percent", 0)
            impact += abs(cost_change) * 1.2

        return min(impact, 100)

    def _generate_item_recommendation(self, item: str, changes: Dict[str, Any]) -> str:
        """Generate recommendation based on item changes."""
        if changes.get("damage", {}).get("change_percent", 0) > 10:
            return f"{item} damage buffed - prioritize in damage builds"
        elif changes.get("cost", {}).get("change_percent", 0) < -10:
            return f"{item} cost reduced - excellent early game value"
        else:
            return f"Monitor {item} performance in upcoming matches"

    def _generate_god_recommendation(self, god: str, changes: Dict[str, Any]) -> str:
        """Generate recommendation based on god changes."""
        if changes.get("ability_damage", {}).get("change_percent", 0) > 15:
            return f"{god} received significant buffs - expect tier increase"
        else:
            return f"Evaluate {god} performance after changes"

    def _calculate_synergy_score(self, matches: List[MatchData], item1: str, item2: str) -> float:
        """Calculate synergy score between two items."""
        total_score = 0.0

        for match in matches:
            # Base score from match outcome
            score = 50 if match.win else 25

            # Bonus for performance metrics
            if match.damage_dealt > 40000:
                score += 15
            if match.damage_mitigated > 20000:
                score += 10
            if (match.kills + match.assists) > match.deaths * 2:
                score += 10

            total_score += score

        return total_score / len(matches) if matches else 0

    def _get_most_relevant_patch(self, patch_versions: List[str]) -> str:
        """Get the most relevant patch from a list."""
        patch_counts: Dict[str, int] = defaultdict(int)
        for patch in patch_versions:
            patch_counts[patch] += 1

        # Weight by recency and frequency
        weighted_scores = {}
        for patch, count in patch_counts.items():
            weight = self.patch_weights.get(patch, 0.1)
            weighted_scores[patch] = count * weight

        return max(weighted_scores.items(), key=lambda x: x[1])[0] if weighted_scores else "OB12"

    def _extract_build_features(
        self, items: List[str], enemy_comp: List[str], patch: str
    ) -> np.ndarray:
        """Extract numerical features for ML prediction."""
        features = []

        # Item features (simplified)
        features.append(len(items))  # Build size
        features.append(sum(1 for i in items if "power" in i.lower()))  # Damage items
        features.append(sum(1 for i in items if "protection" in i.lower()))  # Defense items

        # Enemy composition features
        features.append(len(enemy_comp))  # Enemy team size
        features.append(sum(1 for g in enemy_comp if "mage" in g.lower()))  # Enemy mages
        features.append(sum(1 for g in enemy_comp if "assassin" in g.lower()))  # Enemy assassins

        # Patch weight
        features.append(self.patch_weights.get(patch, 0.5))

        return np.array(features)

    def _logistic_prediction(self, features: np.ndarray, matches: List[MatchData]) -> float:
        """Simple logistic regression prediction."""
        # Simplified implementation - in practice, use sklearn
        base_win_rate = sum(1 for m in matches if m.win) / len(matches)

        # Adjust based on features (simplified heuristic)
        adjustment: float = 0.0
        if features[1] > 3:  # Many damage items
            adjustment += 0.05
        if features[2] > 2:  # Many defense items
            adjustment += 0.03

        return min(max(base_win_rate + adjustment, 0.1), 0.9)

    def _predict_kda(self, features: np.ndarray, matches: List[MatchData]) -> float:
        """Predict KDA based on features."""
        avg_kda = sum((m.kills + m.assists) / max(m.deaths, 1) for m in matches) / len(matches)
        return avg_kda

    def _predict_damage(self, features: np.ndarray, matches: List[MatchData]) -> float:
        """Predict damage output based on features."""
        avg_damage = sum(m.damage_dealt for m in matches) / len(matches)
        return avg_damage

    def _heuristic_prediction(
        self, god: str, role: str, items: List[str], enemy_comp: List[str], patch: str
    ) -> Dict[str, float]:
        """Heuristic prediction when insufficient data."""
        # Base predictions using role averages
        role_baselines = {
            "Mid": {"win_rate": 0.52, "kda": 2.1, "damage": 38000},
            "Carry": {"win_rate": 0.51, "kda": 2.3, "damage": 42000},
            "Support": {"win_rate": 0.50, "kda": 1.8, "damage": 18000},
            "Solo": {"win_rate": 0.49, "kda": 1.9, "damage": 25000},
            "Jungle": {"win_rate": 0.53, "kda": 2.5, "damage": 32000},
        }

        baseline = role_baselines.get(role, {"win_rate": 0.50, "kda": 2.0, "damage": 30000})

        return {
            "win_probability": baseline["win_rate"],
            "predicted_kda": baseline["kda"],
            "predicted_damage": baseline["damage"],
            "confidence": 30,  # Low confidence for heuristic
        }

    def _calculate_consistency(self, build: List[str], enemy_comps: List[List[str]]) -> float:
        """Calculate build consistency across different enemy compositions."""
        # Simplified consistency metric
        return 0.7  # Placeholder

    def _store_synergies(self, synergies: List[ItemSynergy]):
        """Store synergies in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for synergy in synergies:
            cursor.execute(
                """
                INSERT OR REPLACE INTO item_synergies 
                (item1, item2, synergy_score, win_rate_boost, matches_analyzed, 
                 confidence_level, patch_version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    synergy.item1,
                    synergy.item2,
                    synergy.synergy_score,
                    synergy.win_rate_boost,
                    synergy.matches_analyzed,
                    synergy.confidence_level,
                    synergy.patch_relevant,
                ),
            )

        conn.commit()
        conn.close()

    # Data loading methods (for testing and initialization)
    def load_sample_data(self):
        """Load sample data for testing."""
        # Sample match data based on OB12 meta
        sample_matches = [
            MatchData(
                match_id="match_001",
                god_name="Hecate",
                role="Mid",
                items=[
                    "Rod of Tahuti",
                    "Spear of Desolation",
                    "Divine Ruin",
                    "Doom Orb",
                    "Soul Reaver",
                ],
                win=True,
                kills=12,
                deaths=3,
                assists=8,
                damage_dealt=45000,
                damage_mitigated=8000,
                healing=2000,
                match_duration=1800,
                enemy_comp=["Thor", "Artemis", "Ares", "Zeus", "Hercules"],
                patch_version="OB12",
            ),
            MatchData(
                match_id="match_002",
                god_name="Ares",
                role="Support",
                items=[
                    "Gauntlet of Thebes",
                    "Sovereignty",
                    "Heartward Amulet",
                    "Spirit Robe",
                    "Mantle of Discord",
                ],
                win=True,
                kills=2,
                deaths=1,
                assists=15,
                damage_dealt=12000,
                damage_mitigated=35000,
                healing=8000,
                match_duration=2100,
                enemy_comp=["Loki", "Freya", "Khepri", "Hecate", "Bellona"],
                patch_version="OB12",
            ),
        ]

        self.match_data.extend(sample_matches)

        # Sample god performance data
        self.god_performance["Hecate"] = GodPerformance(
            god_name="Hecate",
            role="Mid",
            win_rate=0.57,
            avg_kda=2.4,
            avg_damage=42000,
            avg_mitigated=9000,
            pick_rate=0.23,
            ban_rate=0.15,
            matches_analyzed=1500,
            patch_version="OB12",
            meta_tier="S",
        )
