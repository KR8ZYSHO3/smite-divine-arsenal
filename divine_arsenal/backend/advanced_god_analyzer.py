#!/usr/bin/env python3
"""
🔥 ADVANCED GOD ANALYZER - BADASS EDITION 🔥
Combines god base stats, item synergies, meta templates, and damage simulations
for professional-level build optimization.
"""

import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from database import Database
from divine_arsenal.backend.data_loader import data_loader

logger = logging.getLogger(__name__)


@dataclass
class GodStats:
    """Complete god statistics with scaling."""

    # Base Stats (Level 1)
    base_health: float
    base_mana: float
    base_physical_power: float
    base_magical_power: float
    base_physical_protection: float
    base_magical_protection: float
    base_attack_speed: float
    base_movement_speed: float

    # Scaling Per Level
    health_per_level: float
    mana_per_level: float
    physical_power_per_level: float
    magical_power_per_level: float
    physical_protection_per_level: float
    magical_protection_per_level: float

    # Ability Scaling
    ability_scaling: Dict[str, float]  # e.g., {"1": 0.8, "2": 0.6, "3": 0.4, "4": 1.2}

    def get_stats_at_level(self, level: int) -> Dict[str, float]:
        """Calculate god stats at specific level."""
        return {
            "health": self.base_health + (self.health_per_level * (level - 1)),
            "mana": self.base_mana + (self.mana_per_level * (level - 1)),
            "physical_power": self.base_physical_power
            + (self.physical_power_per_level * (level - 1)),
            "magical_power": self.base_magical_power + (self.magical_power_per_level * (level - 1)),
            "physical_protection": self.base_physical_protection
            + (self.physical_protection_per_level * (level - 1)),
            "magical_protection": self.base_magical_protection
            + (self.magical_protection_per_level * (level - 1)),
            "attack_speed": self.base_attack_speed,
            "movement_speed": self.base_movement_speed,
        }


@dataclass
class ItemSynergy:
    """Advanced item-god synergy calculation."""

    stat_efficiency: float  # How well item stats work with god
    ability_synergy: float  # How well item enhances god's abilities
    playstyle_fit: float  # How well item fits god's playstyle
    power_curve_impact: float  # How much item improves god's power curve
    unique_synergy: float  # Special interactions (e.g., mana scaling)

    @property
    def total_synergy(self) -> float:
        """Calculate overall synergy score."""
        return (
            self.stat_efficiency * 0.3
            + self.ability_synergy * 0.25
            + self.playstyle_fit * 0.2
            + self.power_curve_impact * 0.15
            + self.unique_synergy * 0.1
        )


@dataclass
class MetaTemplate:
    """Professional meta template for god+role combinations."""

    god_name: str
    role: str
    core_items: List[str]  # Must-have items
    situational_items: List[str]  # Good alternatives
    power_spikes: List[Tuple[str, int]]  # (item_name, game_minute)
    win_rate: float
    pick_rate: float
    ban_rate: float
    difficulty: str  # "Easy", "Medium", "Hard"
    counters_well: List[str]  # Gods this build counters
    weak_against: List[str]  # What this build struggles against


class AdvancedGodAnalyzer:
    """🔥 BADASS God Analysis System 🔥"""

    def __init__(self, db: Database):
        self.db = db
        self._init_god_stats()
        self._init_meta_templates()
        self._init_synergy_rules()
        self.items = self._init_items()
        logger.info(f"🔥 Advanced God Analyzer initialized with {len(self.god_stats)} gods and {len(self.items)} items")

    def _init_god_stats(self):
        """Initialize comprehensive god statistics."""
        self.god_stats = self._init_god_stats_from_data()

    def _init_god_stats_from_data(self) -> Dict[str, GodStats]:
        """Initialize god stats from the data loader."""
        gods_data = data_loader.load_gods_data()
        god_stats = {}
        
        for god_name, stats in gods_data.items():
            try:
                god_stats[god_name] = GodStats(
                    base_health=stats.get('base_health', 500),
                    base_mana=stats.get('base_mana', 275),
                    base_physical_power=stats.get('base_physical_power', 35),
                    base_magical_power=stats.get('base_magical_power', 0),
                    base_physical_protection=stats.get('base_physical_protection', 25),
                    base_magical_protection=stats.get('base_magical_protection', 30),
                    base_attack_speed=stats.get('base_attack_speed', 0.9),
                    base_movement_speed=stats.get('base_movement_speed', 375),
                    health_per_level=stats.get('health_per_level', 85),
                    mana_per_level=stats.get('mana_per_level', 50),
                    physical_power_per_level=stats.get('physical_power_per_level', 2.0),
                    magical_power_per_level=stats.get('magical_power_per_level', 0),
                    physical_protection_per_level=stats.get('physical_protection_per_level', 2.5),
                    magical_protection_per_level=stats.get('magical_protection_per_level', 1.5),
                    ability_scaling=stats.get('ability_scaling', {"1": 0.7, "2": 0.6, "3": 0.5, "4": 0.9}),
                )
            except Exception as e:
                logger.warning(f"Failed to load stats for {god_name}: {e}")
                continue
                
        # Add some fallback gods if data loader fails
        if not god_stats:
            god_stats = self._init_fallback_god_stats()
            
        return god_stats

    def _init_items(self) -> List[Dict[str, Any]]:
        """Initialize items from the data loader."""
        items = data_loader.load_items_data()
        
        # Add some fallback items if data loader fails
        if not items:
            items = self._init_fallback_items()
            
        return items

    def _init_fallback_god_stats(self) -> Dict[str, GodStats]:
        """Initialize fallback god stats if data loader fails."""
        return {
            "Zeus": GodStats(
                base_health=470,
                base_mana=320,
                base_physical_power=37,
                base_magical_power=0,
                base_physical_protection=10,
                base_magical_protection=30,
                base_attack_speed=0.9,
                base_movement_speed=355,
                health_per_level=86,
                mana_per_level=60,
                physical_power_per_level=2.3,
                magical_power_per_level=0,
                physical_protection_per_level=2.7,
                magical_protection_per_level=1.6,
                ability_scaling={"1": 0.9, "2": 0.7, "3": 0.5, "4": 1.1},
            ),
            "Anubis": GodStats(
                base_health=500,
                base_mana=275,
                base_physical_power=35,
                base_magical_power=0,
                base_physical_protection=25.16,
                base_magical_protection=36.58,
                base_attack_speed=0.926,
                base_movement_speed=442,
                health_per_level=92,
                mana_per_level=45,
                physical_power_per_level=1.5,
                magical_power_per_level=0,
                physical_protection_per_level=2.84,
                magical_protection_per_level=1.42,
                ability_scaling={"1": 0.22, "2": 0.55, "3": 0.35, "4": 0.9},
            ),
        }

    def _init_fallback_items(self) -> List[Dict[str, Any]]:
        """Initialize fallback items if data loader fails."""
        return [
            {
                "name": "Book of Thoth",
                "cost": 2500,
                "stats": {
                    "magical_power": 100,
                    "mana": 300,
                    "magical_protection": 20,
                }
            },
            {
                "name": "Soul Gem",
                "cost": 2200,
                "stats": {
                    "magical_power": 80,
                    "health": 200,
                    "magical_protection": 15,
                }
            },
            {
                "name": "Divine Ruin",
                "cost": 2300,
                "stats": {
                    "magical_power": 90,
                    "physical_protection": 25,
                }
            },
        ]

    def _init_meta_templates(self):
        """Initialize professional meta templates."""
        self.meta_templates = {
            ("Agni", "Mid"): MetaTemplate(
                god_name="Agni",
                role="Mid",
                core_items=["Book of Thoth", "Rod of Tahuti", "Spear of Desolation"],
                situational_items=["Bancroft's Talon", "Soul Reaver", "Chronos' Pendant"],
                power_spikes=[("Book of Thoth", 8), ("Rod of Tahuti", 15)],
                win_rate=0.67,
                pick_rate=0.12,
                ban_rate=0.05,
                difficulty="Medium",
                counters_well=["Scylla", "Hera"],
                weak_against=["Susano", "Serqet"],
            ),
            ("Achilles", "Solo"): MetaTemplate(
                god_name="Achilles",
                role="Solo",
                core_items=["Gladiator's Shield", "Blackthorn Hammer", "Sovereignty"],
                situational_items=["Shifter's Shield", "Heartward Amulet", "Executioner"],
                power_spikes=[("Gladiator's Shield", 6), ("Blackthorn Hammer", 12)],
                win_rate=0.71,
                pick_rate=0.15,
                ban_rate=0.08,
                difficulty="Hard",
                counters_well=["Tyr", "King Arthur"],
                weak_against=["Chang'e", "Bellona"],
            ),
            # Add more templates...
        }

    def _init_synergy_rules(self):
        """Initialize item-god synergy calculation rules."""
        self.synergy_rules = {
            # Mana Scaling Gods (Book of Thoth synergy)
            "mana_scaling": {
                "gods": ["Agni", "Scylla", "Kukulkan", "Freya"],
                "items": ["Book of Thoth"],
                "synergy_bonus": 1.5,
            },
            # Auto-attack based gods (AS/Crit synergy)
            "auto_attack": {
                "gods": ["Apollo", "Artemis", "Rama"],
                "items": ["Executioner", "Deathbringer", "Wind Demon"],
                "synergy_bonus": 1.3,
            },
            # Ability-based warriors (CDR synergy)
            "ability_warrior": {
                "gods": ["Achilles", "King Arthur", "Tyr"],
                "items": ["Blackthorn Hammer", "Gladiator's Shield"],
                "synergy_bonus": 1.4,
            },
            # High mobility gods (Movement items)
            "mobility": {
                "gods": ["Susano", "Serqet", "Mercury"],
                "items": ["Heartseeker", "Charon's Coin"],
                "synergy_bonus": 1.2,
            },
        }

    def calculate_item_synergy(self, god_name: str, item: Dict[str, Any], role: str) -> ItemSynergy:
        """🔥 Calculate advanced item-god synergy."""
        if god_name not in self.god_stats:
            return ItemSynergy(0.5, 0.5, 0.5, 0.5, 0.5)  # Default neutral

        god_stats = self.god_stats[god_name]
        item_stats = item.get("stats", {})

        # 1. Stat Efficiency (how well item stats complement god stats)
        stat_efficiency = self._calculate_stat_efficiency(god_stats, item_stats, god_name)

        # 2. Ability Synergy (how well item enhances abilities)
        ability_synergy = self._calculate_ability_synergy(god_stats, item, god_name)

        # 3. Playstyle Fit (how well item fits god's intended playstyle)
        playstyle_fit = self._calculate_playstyle_fit(god_name, item, role)

        # 4. Power Curve Impact (how much item improves power progression)
        power_curve_impact = self._calculate_power_curve_impact(god_stats, item, role)

        # 5. Unique Synergy (special interactions)
        unique_synergy = self._calculate_unique_synergy(god_name, item)

        return ItemSynergy(
            stat_efficiency=stat_efficiency,
            ability_synergy=ability_synergy,
            playstyle_fit=playstyle_fit,
            power_curve_impact=power_curve_impact,
            unique_synergy=unique_synergy,
        )

    def _calculate_stat_efficiency(
        self, god_stats: GodStats, item_stats: Dict[str, Any], god_name: str
    ) -> float:
        """Calculate how efficiently item stats work with god's base stats."""
        efficiency = 0.5  # Base efficiency

        # Check for stat scaling synergies
        if "magical_power" in item_stats and god_stats.base_magical_power == 0:
            # Magical power on magical god
            efficiency += min(item_stats["magical_power"] / 200.0, 0.3)

        if "physical_power" in item_stats and god_stats.base_physical_power > 35:
            # Physical power on physical god
            efficiency += min(item_stats["physical_power"] / 100.0, 0.3)

        # Health scaling
        if "health" in item_stats:
            efficiency += min(item_stats["health"] / 600.0, 0.2)

        # Mana synergy with mana-hungry gods
        if "mana" in item_stats and god_stats.base_mana > 300:
            efficiency += min(item_stats["mana"] / 400.0, 0.15)

        return min(efficiency, 1.0)

    def _calculate_ability_synergy(
        self, god_stats: GodStats, item: Dict[str, Any], god_name: str
    ) -> float:
        """Calculate how well item enhances god's abilities."""
        synergy: float = 0.5
        item_stats = item.get("stats", {})

        # CDR synergy for ability-heavy gods
        if "cooldown_reduction" in item_stats:
            avg_scaling = sum(god_stats.ability_scaling.values()) / len(god_stats.ability_scaling)
            if avg_scaling > 0.7:  # High ability scaling god
                synergy += min(item_stats["cooldown_reduction"] / 30.0, 0.25)

        # Penetration synergy for damage dealers
        if "penetration" in item_stats:
            if god_stats.base_magical_power == 0 or god_stats.base_physical_power > 40:
                synergy += min(item_stats["penetration"] / 40.0, 0.2)

        # Attack speed for auto-attack gods
        if "attack_speed" in item_stats and god_stats.base_attack_speed >= 1.0:
            synergy += min(item_stats["attack_speed"] / 50.0, 0.2)

        return min(synergy, 1.0)

    def _calculate_playstyle_fit(self, god_name: str, item: Dict[str, Any], role: str) -> float:
        """Calculate how well item fits god's intended playstyle."""
        fit = 0.5
        item_category = item.get("category", "")

        # Role-based playstyle fitting
        if role == "Mid" and item_category == "Magical":
            fit += 0.3
        elif role == "Solo" and item_category == "Defense":
            fit += 0.3
        elif role == "Carry" and item_category == "Physical":
            fit += 0.3
        elif role == "Support" and item_category in ["Defense", "Starter"]:
            fit += 0.3

        # God-specific playstyle bonuses
        if god_name in ["Agni", "Scylla"] and "magical_power" in item.get("stats", {}):
            fit += 0.2
        elif god_name in ["Apollo", "Artemis"] and "attack_speed" in item.get("stats", {}):
            fit += 0.2

        return min(fit, 1.0)

    def _calculate_power_curve_impact(
        self, god_stats: GodStats, item: Dict[str, Any], role: str
    ) -> float:
        """Calculate how much item improves god's power progression."""
        impact = 0.5
        item_cost = item.get("cost", 1000)
        item_stats = item.get("stats", {})

        # Early game impact (cheaper items)
        if item_cost < 1500:
            impact += 0.2
        elif item_cost > 2500:
            # Late game impact (expensive items should be powerful)
            total_stats = sum(v for v in item_stats.values() if isinstance(v, (int, float)))
            if total_stats > 150:  # High stat total
                impact += 0.3

        # Power spike potential
        if "magical_power" in item_stats and item_stats["magical_power"] > 80:
            impact += 0.2
        elif "physical_power" in item_stats and item_stats["physical_power"] > 60:
            impact += 0.2

        return min(impact, 1.0)

    def _calculate_unique_synergy(self, god_name: str, item: Dict[str, Any]) -> float:
        """Calculate special god-item interactions."""
        synergy = 0.5
        item_name = item.get("name", "")

        # Check synergy rules
        for rule_name, rule in self.synergy_rules.items():
            if god_name in rule["gods"] and item_name in rule["items"]:
                synergy *= rule["synergy_bonus"]

        # Special interactions based on passives
        passive = item.get("passive", "").lower()
        if "mana" in passive and god_name in ["Agni", "Scylla", "Kukulkan"]:
            synergy += 0.3
        elif "critical" in passive and god_name in ["Apollo", "Artemis"]:
            synergy += 0.25
        elif "protection" in passive and god_name in ["Achilles", "Tyr"]:
            synergy += 0.2

        return min(synergy, 1.0)

    def simulate_damage_output(
        self, god_name: str, items: List[Dict[str, Any]], level: int = 20
    ) -> Dict[str, float]:
        """🔥 BADASS Damage Simulation System 🔥"""
        if god_name not in self.god_stats:
            return {"ability_damage": 0, "auto_attack_damage": 0, "dps": 0, "effective_health": 0}

        god_stats = self.god_stats[god_name]
        level_stats = god_stats.get_stats_at_level(level)

        # Add item stats
        total_stats = level_stats.copy()
        for item in items:
            item_stats = item.get("stats", {})
            for stat, value in item_stats.items():
                if stat in total_stats:
                    total_stats[stat] += value

        # Calculate ability damage (average of all abilities)
        ability_damage = 0
        for ability, scaling in god_stats.ability_scaling.items():
            base_damage = 250  # Approximate base damage at level 20
            if total_stats.get("magical_power", 0) > 0:
                ability_damage += base_damage + (total_stats.get("magical_power", 0) * scaling)
            else:
                ability_damage += base_damage + (total_stats.get("physical_power", 0) * scaling)

        ability_damage /= max(1, len(god_stats.ability_scaling))  # Avoid division by zero

        # Calculate auto-attack damage
        if total_stats.get("magical_power", 0) > 0:
            auto_damage = total_stats.get("physical_power", 0) + (total_stats.get("magical_power", 0) * 0.2)
        else:
            auto_damage = total_stats.get("physical_power", 0)

        # Calculate DPS (abilities + autos)
        attack_speed = total_stats.get("attack_speed", 0) + min(total_stats.get("attack_speed", 0), 2.5)
        dps = (auto_damage * attack_speed) + (ability_damage / 3)  # Assume ability every 3 seconds

        # Fallback for missing stats
        health = total_stats.get("health", 0)
        physical_protection = total_stats.get("physical_protection", 0)
        magical_protection = total_stats.get("magical_protection", 0)
        effective_health = health * (1 + (physical_protection + magical_protection) / 200)

        return {
            "ability_damage": ability_damage,
            "auto_attack_damage": auto_damage,
            "dps": dps,
            "effective_health": effective_health,
        }

    def get_meta_template(self, god_name: str, role: str) -> Optional[MetaTemplate]:
        """Get professional meta template for god+role."""
        return self.meta_templates.get((god_name, role))

    def analyze_build_effectiveness(
        self, god_name: str, role: str, items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """🔥 ULTIMATE Build Analysis 🔥"""
        # Get meta template
        template = self.get_meta_template(god_name, role)

        # Calculate synergies
        synergies = []
        total_synergy = 0.0
        for item in items:
            synergy = self.calculate_item_synergy(god_name, item, role)
            synergies.append(synergy)
            total_synergy += synergy.total_synergy

        avg_synergy = total_synergy / len(items) if items else 0

        # Damage simulation
        damage_analysis = self.simulate_damage_output(god_name, items)

        # Meta compliance (how well build matches pro meta)
        meta_compliance = 0.0
        if template:
            core_items_present = sum(1 for item in items if item.get("name") in template.core_items)
            meta_compliance = (
                core_items_present / len(template.core_items) if template.core_items else 0
            )

        return {
            "synergy_score": avg_synergy,
            "damage_analysis": damage_analysis,
            "meta_compliance": meta_compliance,
            "template": template,
            "individual_synergies": synergies,
            "recommendation": self._generate_build_recommendation(
                avg_synergy, meta_compliance, damage_analysis
            ),
        }

    def _generate_build_recommendation(
        self, synergy: float, meta_compliance: float, damage: Dict[str, float]
    ) -> str:
        """Generate intelligent build recommendation."""
        if synergy > 0.8 and meta_compliance > 0.8:
            return "🔥 ELITE BUILD - Professional meta with perfect synergy!"
        elif synergy > 0.7:
            return "💪 STRONG BUILD - Excellent item synergies detected!"
        elif meta_compliance > 0.7:
            return "📊 META BUILD - Follows professional strategies!"
        elif damage["dps"] > 1000:
            return "⚔️ HIGH DAMAGE - Massive damage potential!"
        else:
            return "🔧 NEEDS IMPROVEMENT - Consider better item synergies!"
