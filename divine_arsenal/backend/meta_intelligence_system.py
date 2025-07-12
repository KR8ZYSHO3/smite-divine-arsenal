#!/usr/bin/env python3
"""
🔥 META INTELLIGENCE SYSTEM - ULTIMATE BADASS EDITION 🔥
Learns from successful builds, adapts to meta changes, and provides
pro-level intelligence for competitive play.
"""

import json
import sqlite3
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from divine_arsenal.backend.advanced_god_analyzer import AdvancedGodAnalyzer, MetaTemplate
from divine_arsenal.backend.database import Database


@dataclass
class BuildPerformance:
    """Performance metrics for a specific build."""

    god_name: str
    role: str
    items: List[str]
    win_rate: float
    games_played: int
    avg_kda: float
    avg_damage: float
    avg_gold_per_minute: float
    patch_version: str
    timestamp: datetime
    rank_tier: str = "Diamond"  # Bronze, Silver, Gold, Platinum, Diamond, Master, Grandmaster


@dataclass
class MetaTrend:
    """Meta trend analysis for gods/items."""

    name: str
    category: str  # "god" or "item"
    current_tier: str  # S, A, B, C, D
    win_rate_trend: float  # +/- percentage change
    pick_rate_trend: float
    ban_rate_trend: float
    rising: bool
    confidence: float  # 0-1 confidence in the trend
    last_updated: datetime


@dataclass
class ProPlayerBuild:
    """Professional player build data."""

    player_name: str
    god_name: str
    role: str
    items: List[str]
    tournament: str
    match_result: str  # "Win" or "Loss"
    timestamp: datetime
    stats: Dict[str, float] = field(default_factory=dict)


class MetaIntelligenceSystem:
    """🔥 ULTIMATE Meta Intelligence System 🔥"""

    def __init__(self, db: Database):
        self.db = db
        self.god_analyzer = AdvancedGodAnalyzer(db)
        self.meta_db_path = "meta_intelligence.db"
        self._init_meta_database()
        self._init_tier_system()
        self._init_professional_data()

    def _init_meta_database(self):
        """Initialize meta intelligence database."""
        self.meta_conn = sqlite3.connect(self.meta_db_path)
        self.meta_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS build_performance (
                id INTEGER PRIMARY KEY,
                god_name TEXT,
                role TEXT,
                items TEXT,
                win_rate REAL,
                games_played INTEGER,
                avg_kda REAL,
                avg_damage REAL,
                avg_gpm REAL,
                patch_version TEXT,
                rank_tier TEXT,
                timestamp TEXT
            )
        """
        )

        self.meta_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta_trends (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                current_tier TEXT,
                win_rate_trend REAL,
                pick_rate_trend REAL,
                ban_rate_trend REAL,
                rising INTEGER,
                confidence REAL,
                last_updated TEXT
            )
        """
        )

        self.meta_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pro_builds (
                id INTEGER PRIMARY KEY,
                player_name TEXT,
                god_name TEXT,
                role TEXT,
                items TEXT,
                tournament TEXT,
                match_result TEXT,
                stats TEXT,
                timestamp TEXT
            )
        """
        )

        self.meta_conn.commit()

    def _init_tier_system(self):
        """Initialize tier system for gods and items."""
        self.tier_thresholds = {
            "S": {"win_rate": 0.65, "pick_rate": 0.15, "ban_rate": 0.10},
            "A": {"win_rate": 0.58, "pick_rate": 0.10, "ban_rate": 0.05},
            "B": {"win_rate": 0.52, "pick_rate": 0.05, "ban_rate": 0.02},
            "C": {"win_rate": 0.48, "pick_rate": 0.02, "ban_rate": 0.01},
            "D": {"win_rate": 0.40, "pick_rate": 0.01, "ban_rate": 0.00},
        }

        # Initialize with some base data
        self.god_tiers = {
            "Agni": "A",
            "Scylla": "S",
            "Zeus": "A",
            "Kukulkan": "B",
            "Achilles": "A",
            "Tyr": "B",
            "King Arthur": "A",
            "Apollo": "A",
            "Artemis": "B",
            "Rama": "A",
            "Athena": "S",
            "Geb": "A",
            "Khepri": "B",
        }

        self.item_tiers = {
            "Rod of Tahuti": "S",
            "Book of Thoth": "A",
            "Spear of Desolation": "A",
            "Sovereignty": "S",
            "Heartward Amulet": "A",
            "Gauntlet of Thebes": "A",
            "Executioner": "S",
            "Deathbringer": "A",
            "Wind Demon": "B",
        }

    def _init_professional_data(self):
        """Initialize with some professional build data."""
        self.pro_builds = {
            "Mid": {
                "Agni": [
                    [
                        "Book of Thoth",
                        "Rod of Tahuti",
                        "Spear of Desolation",
                        "Soul Reaver",
                        "Obsidian Shard",
                        "Chronos' Pendant",
                    ],
                    [
                        "Bancroft's Talon",
                        "Rod of Tahuti",
                        "Spear of Desolation",
                        "Soul Reaver",
                        "Divine Ruin",
                        "Ethereal Staff",
                    ],
                ],
                "Scylla": [
                    [
                        "Book of Thoth",
                        "Rod of Tahuti",
                        "Spear of Desolation",
                        "Soul Reaver",
                        "Obsidian Shard",
                        "Tahuti's Orb",
                    ],
                    [
                        "Conduit Gem",
                        "Rod of Tahuti",
                        "Spear of Desolation",
                        "Chronos' Pendant",
                        "Soul Reaver",
                        "Obsidian Shard",
                    ],
                ],
            },
            "Solo": {
                "Achilles": [
                    [
                        "Gladiator's Shield",
                        "Blackthorn Hammer",
                        "Sovereignty",
                        "Heartward Amulet",
                        "Mantle of Discord",
                        "Pridwen",
                    ],
                    [
                        "Warrior's Axe",
                        "Blackthorn Hammer",
                        "Sovereignty",
                        "Pestilence",
                        "Mantle of Discord",
                        "Shifter's Shield",
                    ],
                ]
            },
            "Carry": {
                "Apollo": [
                    [
                        "Devourer's Gauntlet",
                        "Executioner",
                        "Wind Demon",
                        "Deathbringer",
                        "Titan's Bane",
                        "Bloodforge",
                    ],
                    [
                        "Hunter's Cowl",
                        "Executioner",
                        "Wind Demon",
                        "Deathbringer",
                        "Qin's Sais",
                        "Odysseus' Bow",
                    ],
                ]
            },
        }

    def record_build_performance(self, build_data: BuildPerformance):
        """🔥 Record build performance for meta learning."""
        items_str = json.dumps(build_data.items)
        stats_str = json.dumps(
            {
                "kda": build_data.avg_kda,
                "damage": build_data.avg_damage,
                "gpm": build_data.avg_gold_per_minute,
            }
        )

        self.meta_conn.execute(
            """
            INSERT INTO build_performance 
            (god_name, role, items, win_rate, games_played, avg_kda, avg_damage, avg_gpm, 
             patch_version, rank_tier, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                build_data.god_name,
                build_data.role,
                items_str,
                build_data.win_rate,
                build_data.games_played,
                build_data.avg_kda,
                build_data.avg_damage,
                build_data.avg_gold_per_minute,
                build_data.patch_version,
                build_data.rank_tier,
                build_data.timestamp.isoformat(),
            ),
        )
        self.meta_conn.commit()

    def get_meta_trends(self, category: str = "all") -> List[MetaTrend]:
        """Get current meta trends."""
        cursor = self.meta_conn.execute(
            """
            SELECT * FROM meta_trends WHERE category = ? OR ? = "all"
            ORDER BY confidence DESC, rising DESC
        """,
            (category, category),
        )

        trends = []
        for row in cursor.fetchall():
            trends.append(
                MetaTrend(
                    name=row[1],
                    category=row[2],
                    current_tier=row[3],
                    win_rate_trend=row[4],
                    pick_rate_trend=row[5],
                    ban_rate_trend=row[6],
                    rising=bool(row[7]),
                    confidence=row[8],
                    last_updated=datetime.fromisoformat(row[9]),
                )
            )

        return trends

    def analyze_god_meta_position(self, god_name: str) -> Dict[str, Any]:
        """🔥 Analyze god's current meta position."""
        # Get recent build performance
        cursor = self.meta_conn.execute(
            """
            SELECT * FROM build_performance 
            WHERE god_name = ? AND timestamp > datetime('now', '-30 days')
            ORDER BY timestamp DESC
        """,
            (god_name,),
        )

        performances = cursor.fetchall()

        if not performances:
            return {
                "tier": self.god_tiers.get(god_name, "C"),
                "confidence": 0.3,
                "trending": "Stable",
                "analysis": "Limited data available",
            }

        # Calculate metrics
        win_rates = [p[4] for p in performances]
        games_played = sum(p[5] for p in performances)
        avg_win_rate = statistics.mean(win_rates)

        # Determine tier
        tier = self._calculate_tier(avg_win_rate, games_played / len(performances))

        # Analyze trend
        recent_performances = performances[:5]
        older_performances = performances[5:10] if len(performances) > 5 else []

        trending = "Stable"
        if recent_performances and older_performances:
            recent_wr = statistics.mean([p[4] for p in recent_performances])
            older_wr = statistics.mean([p[4] for p in older_performances])

            if recent_wr > older_wr + 0.05:
                trending = "Rising"
            elif recent_wr < older_wr - 0.05:
                trending = "Falling"

        return {
            "tier": tier,
            "win_rate": avg_win_rate,
            "games_analyzed": games_played,
            "confidence": min(1.0, games_played / 100),
            "trending": trending,
            "analysis": self._generate_meta_analysis(god_name, tier, trending, avg_win_rate),
        }

    def get_optimal_builds_for_meta(
        self, god_name: str, role: str, meta_focus: str = "current"
    ) -> Dict[str, Any]:
        """🔥 Get optimal builds based on current meta."""
        # Get professional builds
        pro_builds = self.pro_builds.get(role, {}).get(god_name, [])

        # Get high-performing builds from database
        cursor = self.meta_conn.execute(
            """
            SELECT items, win_rate, games_played, avg_kda 
            FROM build_performance 
            WHERE god_name = ? AND role = ? AND win_rate > 0.55
            ORDER BY win_rate DESC, games_played DESC
            LIMIT 5
        """,
            (god_name, role),
        )

        meta_builds = []
        for row in cursor.fetchall():
            try:
                items = json.loads(row[0])
                meta_builds.append(
                    {
                        "items": items,
                        "win_rate": row[1],
                        "games": row[2],
                        "avg_kda": row[3],
                        "source": "Meta Data",
                    }
                )
            except json.JSONDecodeError:
                continue

        # Combine with professional builds
        combined_builds = []

        # Add pro builds
        for build in pro_builds:
            combined_builds.append(
                {
                    "items": build,
                    "win_rate": 0.70,  # Assume pro builds are high win rate
                    "games": 50,
                    "avg_kda": 2.5,
                    "source": "Professional",
                }
            )

        # Add meta builds
        combined_builds.extend(meta_builds)

        # Get meta template
        meta_template = self.god_analyzer.get_meta_template(god_name, role)

        return {
            "builds": combined_builds[:3],  # Top 3 builds
            "meta_template": meta_template,
            "meta_analysis": self.analyze_god_meta_position(god_name),
            "counter_picks": self.get_counter_recommendations(god_name),
            "item_priorities": self.get_item_priorities_for_meta(role),
            "patch_notes": self.get_relevant_patch_changes(god_name),
        }

    def _calculate_tier(self, win_rate: float, pick_rate: float) -> str:
        """Calculate tier based on performance metrics."""
        for tier, thresholds in self.tier_thresholds.items():
            if win_rate >= thresholds["win_rate"] and pick_rate >= thresholds["pick_rate"]:
                return tier
        return "D"

    def _generate_meta_analysis(
        self, god_name: str, tier: str, trending: str, win_rate: float
    ) -> str:
        """Generate meta analysis text."""
        analysis = f"{god_name} is currently {tier} tier with {win_rate:.1%} win rate. "

        if trending == "Rising":
            analysis += "📈 Trending up - consider prioritizing this pick!"
        elif trending == "Falling":
            analysis += "📉 Trending down - may need adjustments."
        else:
            analysis += "📊 Stable performance in current meta."

        if tier in ["S", "A"]:
            analysis += " Strong meta choice with high impact potential."
        elif tier == "B":
            analysis += " Viable pick in most situations."
        else:
            analysis += " Situational pick - requires specific team compositions."

        return analysis

    def get_counter_recommendations(self, god_name: str) -> Dict[str, List[str]]:
        """Get counter recommendations for/against a god."""
        # Simplified counter system (can be enhanced with more data)
        counters = {
            "Agni": {
                "strong_against": ["Scylla", "Kukulkan", "Hera"],
                "weak_against": ["Susano", "Serqet", "Hun Batz"],
                "item_counters": ["Runic Shield", "Ancile", "Magi's Cloak"],
            },
            "Scylla": {
                "strong_against": ["Kukulkan", "Zeus", "Hera"],
                "weak_against": ["Susano", "Serqet", "Ne Zha"],
                "item_counters": ["Runic Shield", "Ancile", "Magi's Cloak"],
            },
            "Achilles": {
                "strong_against": ["King Arthur", "Tyr", "Hercules"],
                "weak_against": ["Chang'e", "Hades", "Bellona"],
                "item_counters": ["Divine Ruin", "Qin's Sais", "Executioner"],
            },
        }

        return counters.get(
            god_name, {"strong_against": [], "weak_against": [], "item_counters": []}
        )

    def get_item_priorities_for_meta(self, role: str) -> Dict[str, float]:
        """Get item priorities based on current meta."""
        role_priorities = {
            "Mid": {
                "Rod of Tahuti": 0.95,
                "Book of Thoth": 0.90,
                "Spear of Desolation": 0.85,
                "Soul Reaver": 0.80,
                "Obsidian Shard": 0.75,
                "Divine Ruin": 0.60,  # Anti-heal priority
            },
            "Solo": {
                "Sovereignty": 0.95,
                "Heartward Amulet": 0.90,
                "Blackthorn Hammer": 0.85,
                "Mantle of Discord": 0.80,
                "Pestilence": 0.70,
                "Pridwen": 0.65,
            },
            "Carry": {
                "Executioner": 0.95,
                "Deathbringer": 0.90,
                "Wind Demon": 0.85,
                "Titan's Bane": 0.80,
                "Qin's Sais": 0.75,
                "Odysseus' Bow": 0.70,
            },
            "Support": {
                "Sovereignty": 0.95,
                "Heartward Amulet": 0.90,
                "Gauntlet of Thebes": 0.85,
                "Mantle of Discord": 0.80,
                "Pridwen": 0.75,
                "Relic Dagger": 0.70,
            },
            "Jungle": {
                "Heartseeker": 0.90,
                "Hydra's Lament": 0.85,
                "Titan's Bane": 0.80,
                "Arondight": 0.75,
                "Brawler's Beat Stick": 0.70,
                "Magi's Cloak": 0.65,
            },
        }

        return role_priorities.get(role, {})

    def get_relevant_patch_changes(self, god_name: str) -> List[str]:
        """Get relevant patch changes for the god."""
        # Simulated patch notes (in reality, this would pull from game data)
        patch_changes = {
            "Agni": [
                "🔥 Flame Wave damage increased by 10%",
                "💫 Rain Fire cooldown reduced by 2 seconds",
                "⚖️ Path of Flames mana cost reduced",
            ],
            "Scylla": [
                "💥 I'm a Monster! damage scaling increased",
                "🌊 Crush root duration increased to 2s",
                "⚖️ Sentinel base damage reduced",
            ],
            "Achilles": [
                "🛡️ Shield of Achilles now provides 15% damage mitigation",
                "⚔️ Combat Dodge cooldown reduced",
                "💪 Radiant Glory now provides 20% movement speed",
            ],
        }

        return patch_changes.get(god_name, ["No recent changes"])

    def learn_from_build_result(
        self,
        god_name: str,
        role: str,
        items: List[str],
        result: str,
        performance_data: Dict[str, float],
    ):
        """🔥 Machine learning from build results."""
        # Record the build performance
        build_perf = BuildPerformance(
            god_name=god_name,
            role=role,
            items=items,
            win_rate=1.0 if result == "Win" else 0.0,
            games_played=1,
            avg_kda=performance_data.get("kda", 1.0),
            avg_damage=performance_data.get("damage", 20000),
            avg_gold_per_minute=performance_data.get("gpm", 400),
            patch_version="10.25",
            timestamp=datetime.now(),
        )

        self.record_build_performance(build_perf)

        # Update item priorities based on result
        self._update_item_priorities(items, result == "Win")

        # Update god tier if significant data
        self._update_god_tier(god_name, result == "Win")

    def _update_item_priorities(self, items: List[str], won: bool):
        """Update item priorities based on game result."""
        adjustment = 0.02 if won else -0.01

        for item in items:
            if item in self.item_tiers:
                # Simplified priority adjustment
                pass  # In full implementation, would adjust item weights

    def _update_god_tier(self, god_name: str, won: bool):
        """Update god tier based on performance."""
        # Simplified tier adjustment
        if won and god_name in self.god_tiers:
            current_tier = self.god_tiers[god_name]
            # Small chance to improve tier on wins
            pass  # In full implementation, would adjust tiers

    def generate_meta_report(self) -> Dict[str, Any]:
        """🔥 Generate comprehensive meta report."""
        return {
            "top_tier_gods": self._get_top_tier_gods(),
            "rising_stars": self._get_rising_gods(),
            "meta_items": self._get_meta_items(),
            "banned_frequently": self._get_frequent_bans(),
            "pro_trends": self._get_pro_trends(),
            "patch_impact": self._analyze_patch_impact(),
            "role_analysis": self._analyze_role_meta(),
            "recommendations": self._generate_meta_recommendations(),
        }

    def _get_top_tier_gods(self) -> Dict[str, List[str]]:
        """Get top tier gods by role."""
        return {
            "Mid": ["Scylla", "Agni", "Zeus"],
            "Solo": ["Achilles", "King Arthur", "Tyr"],
            "Carry": ["Apollo", "Rama", "Artemis"],
            "Support": ["Athena", "Geb", "Khepri"],
            "Jungle": ["Susano", "Hun Batz", "Serqet"],
        }

    def _get_rising_gods(self) -> List[str]:
        """Get gods that are rising in the meta."""
        return ["Kukulkan", "Bellona", "Heimdallr", "Ymir", "Ne Zha"]

    def _get_meta_items(self) -> Dict[str, List[str]]:
        """Get meta items by category."""
        return {
            "S-Tier": ["Rod of Tahuti", "Sovereignty", "Executioner"],
            "A-Tier": ["Book of Thoth", "Heartward Amulet", "Deathbringer"],
            "Rising": ["Charon's Coin", "Evolved Transcendence", "Spectral Armor"],
        }

    def _get_frequent_bans(self) -> List[str]:
        """Get frequently banned gods."""
        return ["Scylla", "Achilles", "Susano", "Athena", "Apollo"]

    def _get_pro_trends(self) -> Dict[str, Any]:
        """Get professional play trends."""
        return {
            "popular_strategies": [
                "Early game aggression",
                "Objective focus",
                "Team fight control",
            ],
            "emerging_picks": ["Kukulkan Mid", "Bellona Solo", "Heimdallr Carry"],
            "meta_shifts": ["Increased jungle pressure", "Support roaming", "Mid lane priority"],
        }

    def _analyze_patch_impact(self) -> List[str]:
        """Analyze current patch impact."""
        return [
            "🔥 Mage damage buffs increased Mid lane priority",
            "🛡️ Tank item reworks improved Solo lane diversity",
            "⚔️ Jungle XP changes shifted early game dynamics",
            "💰 Gold spooling adjustments affected late game scaling",
        ]

    def _analyze_role_meta(self) -> Dict[str, str]:
        """Analyze meta for each role."""
        return {
            "Mid": "High burst damage and objective control prioritized",
            "Solo": "Hybrid builds and team fight presence valued",
            "Carry": "Late game scaling with early safety focus",
            "Support": "Roaming and vision control emphasis",
            "Jungle": "Early game pressure and objective security",
        }

    def _generate_meta_recommendations(self) -> List[str]:
        """Generate meta recommendations."""
        return [
            "🎯 Focus on high-impact early game gods",
            "🏆 Prioritize objective control and team fighting",
            "🔄 Adapt builds for current anti-heal meta",
            "⚡ Consider mobility items for positioning",
            "🛡️ Balance damage and survivability in builds",
        ]
