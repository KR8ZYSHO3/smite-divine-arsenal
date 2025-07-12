#!/usr/bin/env python3
"""Advanced Build Optimizer with Synergy Analysis and Meta Intelligence."""

import math
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from divine_arsenal.backend.database import Database


@dataclass
class ItemSynergy:
    """Represents synergy between two items."""

    item1: str
    item2: str
    synergy_score: float
    reason: str


@dataclass
class PowerSpike:
    """Represents a power spike in the build."""

    item_index: int
    item_name: str
    spike_type: str  # "Early", "Mid", "Late", "Teamfight", "Solo"
    power_rating: float
    description: str


@dataclass
class BuildAnalysis:
    """Comprehensive build analysis."""

    total_cost: int
    damage_potential: float
    survivability: float
    utility_score: float
    meta_rating: float
    power_spikes: List[PowerSpike]
    synergies: List[ItemSynergy]
    weaknesses: List[str]
    strengths: List[str]
    game_phase_rating: Dict[str, float]  # Early, Mid, Late


class AdvancedBuildOptimizer:
    """Advanced build optimizer with deep game knowledge."""

    def __init__(self, db: Database):
        self.db = db
        self._init_meta_knowledge()
        self._init_item_synergies()
        self._init_counter_matrix()
        self._init_playstyle_scoring()

    def _init_meta_knowledge(self):
        """Initialize current meta item priorities and ratings."""
        self.meta_tiers = {
            # S-Tier Items (Meta defining)
            "Rod of Tahuti": 95,
            "Deathbringer": 92,
            "Book of Thoth": 90,
            "Transcendence": 88,
            "Obsidian Shard": 87,
            "Soul Reaver": 85,
            # A-Tier Items (Very strong)
            "Bancroft's Talon": 82,
            "Blood-Bound Book": 80,
            "Spear of Desolation": 78,
            "Executioner": 85,
            "Qin's Sais": 83,
            "Odysseus' Bow": 81,
            "Breastplate of Valor": 84,
            "Spirit Robe": 82,
            "Mantle of Discord": 80,
            # B-Tier Items (Solid picks)
            "Chronos' Pendant": 75,
            "Divine Ruin": 73,
            "Doom Orb": 71,
            "Devourer's Gauntlet": 77,
            "Asi": 74,
            "Bloodforge": 72,
            "Hide of the Urchin": 76,
            "Genji's Guard": 74,
            "Oni Hunter's Garb": 72,
            # C-Tier Items (Situational)
            "Gem of Focus": 65,
            "Polynomicon": 63,
            "Staff of Myrddin": 61,
            "Ichaival": 67,
            "Toxic Blade": 65,
            "Brawler's Beat Stick": 63,
        }

        # Role meta priorities (what each role should focus on)
        self.role_priorities = {
            "Solo": {"survivability": 0.4, "utility": 0.3, "damage": 0.3},
            "Support": {"utility": 0.5, "survivability": 0.4, "damage": 0.1},
            "Mid": {"damage": 0.6, "utility": 0.2, "survivability": 0.2},
            "Carry": {"damage": 0.7, "survivability": 0.2, "utility": 0.1},
            "Jungle": {"damage": 0.5, "utility": 0.3, "survivability": 0.2},
        }

    def _init_item_synergies(self):
        """Initialize item synergy combinations based on actual database items."""
        self.item_synergies = [
            # Magical Power Synergies (based on actual items)
            ItemSynergy(
                "Book of Thoth",
                "Rod of Tahuti",
                0.95,
                "Mana scaling into percentage power amplification",
            ),
            ItemSynergy(
                "Book of Thoth",
                "Spear of Desolation",
                0.85,
                "High mana pool with penetration and CDR",
            ),
            ItemSynergy(
                "Rod of Tahuti", "Spear of Desolation", 0.9, "Ultimate magical burst combination"
            ),
            # Physical Power Synergies (based on actual items)
            ItemSynergy(
                "Executioner", "Deathbringer", 0.95, "Protection shred amplifies critical damage"
            ),
            ItemSynergy(
                "Devourer's Gauntlet", "Executioner", 0.85, "Sustain with DPS optimization"
            ),
            ItemSynergy("Jotunn's Wrath", "Heartseeker", 0.9, "Ability-based burst synergy"),
            ItemSynergy(
                "Jotunn's Wrath", "The Crusher", 0.8, "Cooldown reduction with ability damage"
            ),
            ItemSynergy(
                "Blackthorn Hammer", "Jotunn's Wrath", 0.75, "Health-based power with cooldown"
            ),
            # Defense Synergies (corrected names)
            ItemSynergy(
                "Sovereignty", "Heartward Amulet", 0.95, "Complete dual-protection aura coverage"
            ),
            ItemSynergy(
                "Gauntlet of Thebes", "Sovereignty", 0.9, "Maximum team protection stacking"
            ),
            ItemSynergy(
                "Gauntlet of Thebes", "Heartward Amulet", 0.9, "Comprehensive support defense"
            ),
            ItemSynergy(
                "Gladiator's Shield", "Blackthorn Hammer", 0.8, "Hybrid defense/offense synergy"
            ),
            ItemSynergy(
                "Shifter's Shield", "Blackthorn Hammer", 0.75, "Adaptive power with health scaling"
            ),
            # Starter to Core Item Progressions
            ItemSynergy(
                "Guardian's Blessing",
                "Gauntlet of Thebes",
                0.85,
                "Support progression optimization",
            ),
            ItemSynergy(
                "Warrior's Blessing", "Gladiator's Shield", 0.8, "Solo lane survivability combo"
            ),
            ItemSynergy(
                "Mage's Blessing", "Book of Thoth", 0.85, "Early mana advantage into late scaling"
            ),
            ItemSynergy(
                "Hunter's Blessing", "Devourer's Gauntlet", 0.9, "ADC power curve optimization"
            ),
            ItemSynergy(
                "Assassin's Blessing", "Jotunn's Wrath", 0.85, "Jungle burst and mobility setup"
            ),
            # Advanced Cross-Category Synergies
            ItemSynergy(
                "Book of Thoth", "Gauntlet of Thebes", 0.65, "Mana-tank hybrid for magical solo"
            ),
            ItemSynergy(
                "Devourer's Gauntlet", "Shifter's Shield", 0.7, "ADC with defensive adaptation"
            ),
            ItemSynergy("Spear of Desolation", "Heartseeker", 0.6, "Mixed penetration synergy"),
            ItemSynergy("Executioner", "Gladiator's Shield", 0.7, "Physical DPS with defense"),
            ItemSynergy(
                "Rod of Tahuti", "Heartward Amulet", 0.6, "Magical carry with team utility"
            ),
        ]

    def _init_counter_matrix(self):
        """Initialize god countering item matrix."""
        self.god_counters = {
            # High heal gods
            "Hel": ["Divine Ruin", "Brawler's Beat Stick", "Pestilence"],
            "Aphrodite": ["Divine Ruin", "Brawler's Beat Stick", "Pestilence"],
            "Ra": ["Divine Ruin", "Brawler's Beat Stick"],
            # High mobility gods
            "Loki": ["Mystical Mail", "Midgardian Mail", "Witchblade"],
            "Mercury": ["Midgardian Mail", "Witchblade", "Frostbound Hammer"],
            "Serqet": ["Magi's Cloak", "Spirit Robe", "Mantle of Discord"],
            # High burst gods
            "Zeus": ["Magi's Cloak", "Spirit Robe", "Mantle of Discord"],
            "Scylla": ["Magi's Cloak", "Spirit Robe", "Ancile"],
            "Thor": ["Physical Protection", "Midgardian Mail"],
            # Crit-based gods
            "Artemis": ["Spectral Armor", "Thorns", "Nemean Lion"],
            "Jing Wei": ["Spectral Armor", "Thorns", "Midgardian Mail"],
        }

    def _init_playstyle_scoring(self):
        """Initialize playstyle scoring system for item optimization."""
        self.playstyle_item_weights = {
            # Damage Focus Playstyles
            "max_damage": {
                "keywords": [
                    "power",
                    "damage",
                    "rod",
                    "book",
                    "staff",
                    "deathbringer",
                    "transcendence",
                ],
                "stats": ["physical_power", "magical_power"],
                "multiplier": 2.0,
            },
            "critical_strike": {
                "keywords": ["crit", "rage", "deathbringer", "wind", "malice"],
                "stats": ["critical_chance", "critical_damage"],
                "multiplier": 2.5,
            },
            "penetration": {
                "keywords": ["penetration", "obsidian", "titan", "executioner", "void"],
                "stats": ["physical_penetration", "magical_penetration"],
                "multiplier": 2.0,
            },
            "attack_speed": {
                "keywords": ["bow", "speed", "hastened", "odysseus", "ichaival"],
                "stats": ["attack_speed"],
                "multiplier": 2.2,
            },
            # Defense Focus Playstyles
            "max_hp": {
                "keywords": ["health", "urchin", "thebes", "gauntlet", "valor"],
                "stats": ["health"],
                "multiplier": 2.5,
            },
            "max_defense": {
                "keywords": ["protection", "breastplate", "genji", "sovereignty", "heartward"],
                "stats": ["physical_protection", "magical_protection"],
                "multiplier": 2.0,
            },
            "anti_burst": {
                "keywords": ["magi", "spirit", "mantle", "discord", "ancile"],
                "stats": ["crowd_control_reduction", "damage_mitigation"],
                "multiplier": 2.0,
            },
            "sustain": {
                "keywords": ["lifesteal", "asi", "bloodforge", "bancroft", "devourer"],
                "stats": ["lifesteal", "magical_lifesteal"],
                "multiplier": 2.2,
            },
            # Utility Focus Playstyles
            "cooldown_reduction": {
                "keywords": ["cooldown", "jotunn", "chronos", "breastplate", "genji"],
                "stats": ["cooldown_reduction"],
                "multiplier": 2.0,
            },
            "mobility": {
                "keywords": ["movement", "speed", "winged", "hastened", "talaria"],
                "stats": ["movement_speed"],
                "multiplier": 1.8,
            },
            "utility_support": {
                "keywords": ["aura", "sovereignty", "heartward", "thebes", "relic"],
                "stats": ["mana", "mp5"],
                "multiplier": 1.5,
            },
            "anti_heal": {
                "keywords": ["heal", "divine", "ruin", "brawler", "pestilence"],
                "stats": ["anti_heal"],
                "multiplier": 3.0,
            },
            # Timing Focus Playstyles
            "early_game": {"cost_range": (0, 2500), "multiplier": 2.0},
            "late_scaling": {"cost_range": (3000, 5000), "multiplier": 2.5},
            "power_spike": {"cost_range": (2000, 3500), "multiplier": 2.2},
            "cost_efficient": {"value_threshold": 100, "multiplier": 1.8},  # cost efficiency score
        }

    def _score_item_for_playstyles(self, item: Dict[str, Any], playstyles: List[str]) -> float:
        """Score an item based on how well it matches the selected playstyles."""
        if not playstyles:
            return 1.0  # Base score if no playstyles selected

        total_score = 0.0
        item_name = item.get("name", "").lower()
        item_stats = item.get("stats", {})
        item_cost = item.get("cost", 0)

        for playstyle in playstyles:
            playstyle_config = self.playstyle_item_weights.get(playstyle, {})
            if not playstyle_config:
                continue

            playstyle_score = 0.0
            multiplier = playstyle_config.get("multiplier", 1.0)

            # Check keywords in item name
            keywords = playstyle_config.get("keywords", [])
            for keyword in keywords:
                if keyword in item_name:
                    playstyle_score += 1.0

            # Check relevant stats
            stats = playstyle_config.get("stats", [])
            for stat in stats:
                if stat in item_stats and item_stats[stat] > 0:
                    playstyle_score += 1.5

            # Check cost range for timing playstyles
            if "cost_range" in playstyle_config:
                min_cost, max_cost = playstyle_config["cost_range"]
                if min_cost <= item_cost <= max_cost:
                    playstyle_score += 2.0

            # Check cost efficiency for cost_efficient playstyle
            if playstyle == "cost_efficient" and item_cost > 0:
                # Simple cost efficiency: total stats value / cost
                stats_value = sum(item_stats.values()) if item_stats else 0
                efficiency = stats_value / item_cost * 1000  # Scale for readability
                threshold = playstyle_config.get("value_threshold", 100)
                if efficiency >= threshold:
                    playstyle_score += 1.5

            # Apply multiplier and add to total
            total_score += playstyle_score * multiplier

        # Normalize score based on number of playstyles to prevent over-weighting
        normalized_score = total_score / len(playstyles) if playstyles else 1.0
        return max(0.1, normalized_score)  # Minimum score to prevent division by zero

    def optimize_build(
        self,
        god_name: str,
        role: str,
        enemy_comp: Optional[List[str]] = None,
        game_phase: str = "All",
        budget: int = 15000,
        playstyles: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Advanced build optimization with comprehensive analysis."""
        try:
            # Get god information
            god = self.db.get_god(god_name)
            if not god:
                return {"error": f"God '{god_name}' not found"}

            # Multi-stage optimization process
            # Stage 1: Generate candidate builds using different strategies
            candidate_builds = self._generate_candidate_builds(god, role, playstyles, budget)

            # Stage 2: Apply enemy composition adjustments
            if enemy_comp:
                candidate_builds = [
                    self._apply_enemy_counters(build, enemy_comp) for build in candidate_builds
                ]

            # Stage 3: Optimize for game phase
            candidate_builds = [
                self._optimize_for_phase(build, game_phase, budget) for build in candidate_builds
            ]

            # Stage 4: Score all candidate builds and select the best
            best_build = self._select_optimal_build(candidate_builds, god, role)

            # Stage 5: Final enhancement with synergies
            final_build = self._enhance_with_synergies(best_build)

            # Generate comprehensive analysis
            analysis = self._analyze_build_comprehensive(final_build, role, god)

            # Generate build order
            build_order = self._generate_build_order(final_build, role)

            # Calculate total cost
            total_cost = sum(item.get("cost", 0) for item in final_build)

            # Generate meta score
            meta_score = self._calculate_meta_score(final_build)

            return {
                "items": [item["name"] for item in final_build],
                "build_order": [item["name"] for item in build_order],
                "total_cost": total_cost,
                "analysis": analysis,
                "meta_score": meta_score,
                "alternatives": self._generate_alternatives(final_build, enemy_comp),
                "power_spikes": analysis.power_spikes,
                "synergies": analysis.synergies,
                "build_explanation": self._generate_build_explanation(analysis, role, god_name),
                "optimization_details": {
                    "candidates_tested": len(candidate_builds),
                    "optimization_strategy": "Multi-permutation statistical analysis",
                    "role_focus": role,
                    "god_compatibility": self._calculate_god_build_compatibility(god, final_build),
                },
            }

        except Exception as e:
            return {"error": f"Advanced optimization failed: {e}"}

    def _generate_candidate_builds(
        self, god: Dict[str, Any], role: str, playstyles: Optional[List[str]], budget: int
    ) -> List[List[Dict[str, Any]]]:
        """Generate multiple candidate builds using different optimization strategies."""
        candidates = []

        # Strategy 1: Pure statistical approach (highest scoring items)
        statistical_build = self._generate_role_build(role, god, playstyles)
        candidates.append(statistical_build)

        # Strategy 2: Meta-focused build (emphasize current meta items)
        meta_build = self._generate_meta_focused_build(role, god, playstyles)
        candidates.append(meta_build)

        # Strategy 3: Synergy-optimized build (maximize item synergies)
        synergy_build = self._generate_synergy_optimized_build(role, god, playstyles)
        candidates.append(synergy_build)

        # Strategy 4: Cost-efficient build (optimize for gold value)
        efficient_build = self._generate_cost_efficient_build(role, god, budget)
        candidates.append(efficient_build)

        # Strategy 5: Balanced hybrid approach
        balanced_build = self._generate_balanced_build(role, god, playstyles, budget)
        candidates.append(balanced_build)

        return candidates

    def _generate_meta_focused_build(
        self, role: str, god: Dict[str, Any], playstyles: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Generate build focusing on current meta items."""
        all_items = self.db.get_all_items()
        damage_type = god.get("damage_type", "Physical")

        # Score items with heavy meta weighting
        item_scores = []
        for item in all_items:
            base_score = self._calculate_comprehensive_item_score(
                item, role, damage_type, god.get("class", ""), playstyles, god
            )
            meta_weight = self.meta_tiers.get(item["name"], 50) / 100
            combined_score = (base_score * 0.3) + (meta_weight * 0.7)  # Heavy meta emphasis
            item_scores.append((item, combined_score))

        item_scores.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in item_scores[:6]]

    def _generate_synergy_optimized_build(
        self, role: str, god: Dict[str, Any], playstyles: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Generate build that maximizes item synergies."""
        all_items = self.db.get_all_items()
        damage_type = god.get("damage_type", "Physical")

        # Find items with high synergy potential
        synergy_scores = {}
        for item in all_items:
            synergy_count = sum(
                1 for s in self.item_synergies if s.item1 == item["name"] or s.item2 == item["name"]
            )
            synergy_scores[item["name"]] = synergy_count

        # Build around high-synergy items
        selected_items: List[Dict[str, Any]] = []
        remaining_items = all_items.copy()

        while len(selected_items) < 6 and remaining_items:
            best_item = None
            best_score = -1

            for item in remaining_items:
                # Calculate synergy with already selected items
                synergy_bonus = 0
                for selected in selected_items:
                    for synergy in self.item_synergies:
                        if (
                            synergy.item1 == item["name"] and synergy.item2 == selected["name"]
                        ) or (synergy.item2 == item["name"] and synergy.item1 == selected["name"]):
                            synergy_bonus += synergy.synergy_score

                base_fitness = self._calculate_statistical_role_fit(item, role, damage_type)
                total_score: float = float(base_fitness + synergy_bonus)

                if total_score > best_score:
                    best_score = total_score
                    best_item = item

            if best_item:
                selected_items.append(best_item)
                remaining_items.remove(best_item)

        return selected_items

    def _generate_cost_efficient_build(
        self, role: str, god: Dict[str, Any], budget: int
    ) -> List[Dict[str, Any]]:
        """Generate the most cost-efficient build within budget."""
        all_items = self.db.get_all_items()
        damage_type = god.get("damage_type", "Physical")

        # Filter items within budget
        affordable_items = [item for item in all_items if item.get("cost", 0) <= budget // 3]

        # Score by cost efficiency
        efficiency_scores = []
        for item in affordable_items:
            role_fit = self._calculate_statistical_role_fit(item, role, damage_type)
            cost_eff = self._calculate_cost_efficiency(item, role)
            stat_eff = self._calculate_stat_efficiency(item, role)

            efficiency_score = (role_fit * 0.4) + (cost_eff * 0.35) + (stat_eff * 0.25)
            efficiency_scores.append((item, efficiency_score))

        efficiency_scores.sort(key=lambda x: x[1], reverse=True)

        # Select items without exceeding budget
        selected_items: List[Dict[str, Any]] = []
        total_cost = 0.0

        for item, score in efficiency_scores:
            if len(selected_items) >= 6:
                break
            if total_cost + item.get("cost", 0) <= budget:
                selected_items.append(item)
                total_cost += item.get("cost", 0)

        # Fill remaining slots with cheapest viable options
        while len(selected_items) < 6:
            remaining = [item for item in affordable_items if item not in selected_items]
            if remaining:
                cheapest = min(remaining, key=lambda x: x.get("cost", 0))
                if total_cost + cheapest.get("cost", 0) <= budget:
                    selected_items.append(cheapest)
                    total_cost += cheapest.get("cost", 0)
                else:
                    break
            else:
                break

        return selected_items

    def _generate_balanced_build(
        self, role: str, god: Dict[str, Any], playstyles: Optional[List[str]], budget: int
    ) -> List[Dict[str, Any]]:
        """Generate a balanced build considering all factors equally."""
        all_items = self.db.get_all_items()
        damage_type = god.get("damage_type", "Physical")

        balanced_scores = []
        for item in all_items:
            # Equal weighting of all factors
            role_fit = self._calculate_statistical_role_fit(item, role, damage_type)
            stat_eff = self._calculate_stat_efficiency(item, role)
            meta_score = self.meta_tiers.get(item["name"], 50) / 100
            cost_eff = self._calculate_cost_efficiency(item, role)
            synergy_pot = self._calculate_synergy_potential(item, role)

            # Playstyle consideration
            playstyle_score = 1.0
            if playstyles:
                playstyle_score = self._score_item_for_playstyles(item, playstyles)

            # God scaling synergy
            scaling_synergy = self._calculate_god_scaling_synergy(item, god)

            balanced_score = (
                role_fit
                + stat_eff
                + meta_score
                + cost_eff
                + synergy_pot
                + playstyle_score
                + scaling_synergy
            ) / 7
            balanced_scores.append((item, balanced_score))

        balanced_scores.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in balanced_scores[:6]]

    def _select_optimal_build(
        self, candidate_builds: List[List[Dict[str, Any]]], god: Dict[str, Any], role: str
    ) -> List[Dict[str, Any]]:
        """Select the best build from candidates using comprehensive scoring."""
        if not candidate_builds:
            return []

        best_build = None
        best_score = -1.0

        for build in candidate_builds:
            if not build:
                continue

            # Comprehensive build evaluation
            build_score = self._evaluate_complete_build(build, god, role)

            if build_score > best_score:
                best_score = build_score
                best_build = build

        return best_build or candidate_builds[0]

    def _evaluate_complete_build(
        self, build: List[Dict[str, Any]], god: Dict[str, Any], role: str
    ) -> float:
        """Evaluate a complete build with comprehensive scoring."""
        if not build:
            return 0.0

        # Individual item quality
        item_quality = sum(
            self._calculate_comprehensive_item_score(
                item, role, god.get("damage_type", "Physical"), god.get("class", ""), None, god
            )
            for item in build
        ) / len(build)

        # Synergy strength
        synergy_strength = self._calculate_build_synergy_strength(build)

        # Role appropriateness
        role_fit = sum(
            self._calculate_statistical_role_fit(item, role, god.get("damage_type", "Physical"))
            for item in build
        ) / len(build)

        # Diversity (avoid too many similar items)
        diversity_score = self._calculate_build_diversity(build)

        # Cost efficiency
        cost_efficiency = sum(self._calculate_cost_efficiency(item, role) for item in build) / len(
            build
        )

        # Meta viability
        meta_viability = sum(self.meta_tiers.get(item["name"], 50) for item in build) / (
            len(build) * 100
        )

        # Combined score with weights
        total_score = (
            item_quality * 0.25
            + synergy_strength * 0.20
            + role_fit * 0.20
            + diversity_score * 0.15
            + cost_efficiency * 0.10
            + meta_viability * 0.10
        )

        return total_score

    def _calculate_build_synergy_strength(self, build: List[Dict[str, Any]]) -> float:
        """Calculate overall synergy strength of a build."""
        item_names = [item["name"] for item in build]
        synergy_score = 0.0
        synergy_count = 0

        for synergy in self.item_synergies:
            if synergy.item1 in item_names and synergy.item2 in item_names:
                synergy_score += synergy.synergy_score
                synergy_count += 1

        # Normalize by build size and possible synergies
        max_possible_synergies = len(build) * (len(build) - 1) // 2
        if max_possible_synergies == 0:
            return 0.5

        return min(1.0, synergy_score / max_possible_synergies)

    def _calculate_build_diversity(self, build: List[Dict[str, Any]]) -> float:
        """Calculate diversity score to avoid over-stacking similar items."""
        if not build:
            return 0.0

        categories = [item.get("category", "Unknown") for item in build]
        unique_categories = len(set(categories))

        # Penalty for too many items in same category
        category_distribution: Dict[str, int] = {}
        for category in categories:
            category_distribution[category] = category_distribution.get(category, 0) + 1

        # Ideal is good spread across categories
        diversity_penalty = 0.0
        for count in category_distribution.values():
            if count > 2:  # More than 2 items in same category
                diversity_penalty += (count - 2) * 0.1

        base_diversity = unique_categories / len(build)
        return max(0.1, base_diversity - diversity_penalty)

    def _calculate_god_build_compatibility(
        self, god: Dict[str, Any], build: List[Dict[str, Any]]
    ) -> float:
        """Calculate how well the build matches the god's characteristics."""
        if not build:
            return 0.0

        god_damage_type = god.get("damage_type", "Physical")
        god_class = god.get("class", "Unknown")

        compatibility_score = 0.0

        for item in build:
            # Damage type compatibility
            item_category = item.get("category", "")
            if (god_damage_type == "Physical" and item_category == "Physical") or (
                god_damage_type == "Magical" and item_category == "Magical"
            ):
                compatibility_score += 0.2

            # Class synergy
            class_synergy = self._calculate_class_synergy(item, god_class, god_damage_type)
            compatibility_score += class_synergy * 0.15

        return min(1.0, compatibility_score / len(build))

    def _generate_build_explanation(
        self, analysis: "BuildAnalysis", role: str, god_name: str
    ) -> str:
        """Generate detailed explanation of build choices."""
        explanations = []

        # Role-specific explanation
        role_explanations = {
            "Solo": f"This {god_name} Solo build emphasizes survivability and utility to dominate the side lane.",
            "Support": f"This {god_name} Support build focuses on team utility and protection to enable your carries.",
            "Mid": f"This {god_name} Mid build maximizes burst potential and objective control for team fights.",
            "Carry": f"This {god_name} Carry build optimizes DPS output and scaling for late game dominance.",
            "Jungle": f"This {god_name} Jungle build balances burst damage with mobility for effective ganking.",
        }

        explanations.append(
            role_explanations.get(
                role, f"This {god_name} build is optimized for {role} effectiveness."
            )
        )

        # Power spike explanation
        if analysis.power_spikes:
            main_spike = analysis.power_spikes[0]
            explanations.append(
                f"Key power spike occurs at {main_spike.item_name} ({main_spike.spike_type})."
            )

        # Strength highlights
        if analysis.strengths:
            top_strengths = analysis.strengths[:2]
            explanations.append(f"Build excels at: {', '.join(top_strengths)}.")

        # Meta rating context
        if analysis.meta_rating > 0.8:
            explanations.append("This build aligns with current meta trends.")
        elif analysis.meta_rating > 0.6:
            explanations.append("This build offers solid viability in the current meta.")
        else:
            explanations.append("This build prioritizes god synergy over meta conformity.")

        return " ".join(explanations)

    def _generate_role_build(
        self, role: str, god: Dict[str, Any], playstyles: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Generate optimal build using statistical analysis and dynamic role scoring."""
        all_items = self.db.get_all_items()

        # Get god characteristics for optimization
        damage_type = god.get("damage_type", "Physical")
        god_class = god.get("class", "Unknown")

        # Statistical analysis: Score each item for the role using multiple criteria
        item_scores = []
        for item in all_items:
            score = self._calculate_comprehensive_item_score(
                item, role, damage_type, god_class, playstyles, god
            )
            item_scores.append((item, score))

        # Sort items by score (highest first)
        item_scores.sort(key=lambda x: x[1], reverse=True)

        # Advanced selection algorithm with diversity and synergy consideration
        selected_items = []
        used_categories: Set[str] = set()

        # Phase 1: Core items (highest scoring items that fit role requirements)
        core_items = self._select_core_items(item_scores, role, damage_type, 2)
        selected_items.extend(core_items)
        used_categories.update(item.get("category", "Unknown") for item in core_items)

        # Phase 2: Complementary items (fill role-specific needs)
        complement_items = self._select_complementary_items(item_scores, role, selected_items, 2)
        selected_items.extend(complement_items)

        # Phase 3: Situational/synergy items (optimize for synergies and meta)
        remaining_slots = 6 - len(selected_items)
        if remaining_slots > 0:
            synergy_items = self._select_synergy_items(item_scores, selected_items, remaining_slots)
            selected_items.extend(synergy_items)

        # Ensure we have exactly 6 items, filling with best available if needed
        while len(selected_items) < 6:
            for item, score in item_scores:
                if item not in selected_items:
                    selected_items.append(item)
                    break

        return selected_items[:6]

    def _calculate_comprehensive_item_score(
        self,
        item: Dict[str, Any],
        role: str,
        damage_type: str,
        god_class: str,
        playstyles: Optional[List[str]] = None,
        god: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate comprehensive item score using statistical analysis and god scaling."""

        # DEBUG: Log every call to see what data we're working with
        with open("scaling_debug.log", "a", encoding="utf-8") as f:
            f.write(
                f"[DEBUG] Scoring {item.get('name', 'Unknown')} for god: {god.get('name', 'Unknown') if god else 'None'}\n"
            )
            f.write(
                f"[DEBUG] God intelligence: {god.get('intelligence', 'None') if god else 'None'}, strength: {god.get('strength', 'None') if god else 'None'}\n"
            )
            f.write(
                f"[DEBUG] Item tags: {item.get('tags', 'None')}, stats: {item.get('stats', 'None')}\n"
            )
            f.write(f"[DEBUG] Role: {role}, damage_type: {damage_type}\n")
            f.write("-" * 50 + "\n")

        # Base scores for different aspects
        role_fitness = self._calculate_statistical_role_fit(item, role, damage_type)
        stat_efficiency = self._calculate_stat_efficiency(item, role)
        meta_score = self.meta_tiers.get(item["name"], 50) / 100  # Normalize to 0-1
        cost_efficiency = self._calculate_cost_efficiency(item, role)
        synergy_potential = self._calculate_synergy_potential(item, role)

        # 🔥 GOD SCALING ANALYSIS - BOOSTED! 🔥
        scaling_synergy = self._calculate_god_scaling_synergy(item, god) if god else 0.0

        # Strong penalty for mismatched item types
        penalty = 0.0
        if god:
            god_stats = god.get("stats", {})
            intelligence = god_stats.get("intelligence", 0)
            strength = god_stats.get("strength", 0)
            item_stats = item.get("stats", {})
            item_tags = item.get("tags", [])
            # If god is magical (intelligence) and item is physical, penalize
            if intelligence and not strength:
                if "Physical" in item_tags or "physical_power" in item_stats:
                    penalty = -1.0
            # If god is physical (strength) and item is magical, penalize
            if strength and not intelligence:
                if "Magical" in item_tags or "magical_power" in item_stats:
                    penalty = -1.0

        # Playstyle scoring if specified
        playstyle_score = 1.0
        if playstyles:
            playstyle_score = self._score_item_for_playstyles(item, playstyles)

        # Category bonus based on role requirements
        category_bonus = self._calculate_category_bonus(item, role)

        # God class synergy (e.g., Warrior items for Warrior gods)
        class_synergy = self._calculate_class_synergy(item, god_class, damage_type)

        # Weighted comprehensive score with scaling EMPHASIS
        comprehensive_score = (
            role_fitness * 0.10  # How well item fits the role
            + stat_efficiency * 0.10  # Statistical efficiency of item stats
            + scaling_synergy * 0.55  # 🔥 GOD SCALING SYNERGY (VERY HIGH PRIORITY)
            + meta_score * 0.05  # Current meta viability
            + cost_efficiency * 0.05  # Gold efficiency
            + synergy_potential * 0.05  # Potential for item synergies
            + playstyle_score * 0.04  # Playstyle compatibility
            + category_bonus * 0.03  # Category appropriateness
            + class_synergy * 0.03  # God class synergy
        )
        comprehensive_score += penalty
        # Debug logging for scaling
        if god:
            log_line = f"God: {god.get('name')} | Int: {god_stats.get('intelligence')} | Str: {god_stats.get('strength')} | Item: {item.get('name')} | Scaling Synergy: {scaling_synergy:.2f} | Penalty: {penalty}\n"
            log_path = os.path.join(os.getcwd(), "scaling_debug.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_line)
        return max(0.01, comprehensive_score)  # Minimum score for stability

    def _calculate_god_scaling_synergy(self, item: Dict[str, Any], god: Dict[str, Any]) -> float:
        """Calculate how well an item synergizes with the god's Intelligence/Strength scaling."""
        if not god:
            return 0.0

        # Get god's scaling data
        god_stats = god.get("stats", {})
        scaling_info = god.get("scaling_info", {})

        # Extract Intelligence and Strength values
        intelligence = god_stats.get("intelligence", 0)
        strength = god_stats.get("strength", 0)

        # If no scaling data, return base score
        if not intelligence and not strength:
            return 0.5

        # Get item stats that could benefit from scaling
        item_stats = item.get("stats", {})
        item_name = item.get("name", "").lower()

        synergy_score = 0.0

        # Intelligence scaling synergy (for magical damage and ability power)
        if intelligence:
            int_value = self._parse_scaling_value(intelligence)
            if int_value > 0:
                # Items that benefit from Intelligence
                if "magical_power" in item_stats:
                    synergy_score += (item_stats["magical_power"] / 100.0) * (int_value / 10.0)
                if "cooldown_reduction" in item_stats:
                    synergy_score += 0.3 * (int_value / 10.0)  # CDR helps with ability spam
                if "mana" in item_stats:
                    synergy_score += 0.2 * (int_value / 10.0)  # Mana helps with ability usage
                if any(keyword in item_name for keyword in ["rod", "staff", "book", "magical"]):
                    synergy_score += 0.4 * (int_value / 10.0)  # Magical items

        # Strength scaling synergy (for physical damage and auto attacks)
        if strength:
            str_value = self._parse_scaling_value(strength)
            if str_value > 0:
                # Items that benefit from Strength
                if "physical_power" in item_stats:
                    synergy_score += (item_stats["physical_power"] / 100.0) * (str_value / 10.0)
                if "attack_speed" in item_stats:
                    synergy_score += 0.3 * (str_value / 10.0)  # Attack speed with physical damage
                if "critical_chance" in item_stats:
                    synergy_score += 0.3 * (str_value / 10.0)  # Crit with physical damage
                if any(keyword in item_name for keyword in ["sword", "axe", "bow", "physical"]):
                    synergy_score += 0.4 * (str_value / 10.0)  # Physical items

        # Role-specific scaling bonuses
        god_role = god.get("role", "").lower()
        if "mid" in god_role and intelligence:
            # Mid laners benefit more from Intelligence
            synergy_score *= 1.2
        elif "carry" in god_role and strength:
            # Carries benefit more from Strength
            synergy_score *= 1.2
        elif "jungle" in god_role:
            # Junglers can benefit from both
            synergy_score *= 1.1

        return min(1.0, synergy_score)

    def _parse_scaling_value(self, scaling_str: str) -> float:
        """Parse scaling value from string (e.g., '5', '10', '15') to float."""
        try:
            # Remove any non-numeric characters and convert to float
            import re

            numbers = re.findall(r"\d+", str(scaling_str))
            if numbers:
                return float(numbers[0])
        except (ValueError, TypeError):
            pass
        return 0.0

    def _calculate_statistical_role_fit(
        self, item: Dict[str, Any], role: str, damage_type: str
    ) -> float:
        """Calculate how well an item fits a role using statistical analysis of its attributes."""
        stats = item.get("stats", {})
        category = item.get("category", "")
        tags = item.get("tags", [])

        # Role-specific stat priorities (based on professional SMITE 2 analysis)
        role_stat_weights = {
            "Solo": {
                "physical_protection": 0.25,
                "magical_protection": 0.25,
                "health": 0.20,
                "cooldown_reduction": 0.15,
                "physical_power": 0.08,
                "magical_power": 0.07,
            },
            "Support": {
                "physical_protection": 0.20,
                "magical_protection": 0.20,
                "health": 0.25,
                "cooldown_reduction": 0.15,
                "mp5": 0.10,
                "movement_speed": 0.05,
                "mana": 0.05,
            },
            "Mid": {
                "magical_power": 0.35 if damage_type == "Magical" else 0.05,
                "physical_power": 0.35 if damage_type == "Physical" else 0.05,
                "penetration": 0.20,
                "cooldown_reduction": 0.15,
                "mana": 0.15,
                "magical_protection": 0.10,
            },
            "Carry": {
                "physical_power": 0.30,
                "attack_speed": 0.25,
                "critical_chance": 0.20,
                "lifesteal": 0.15,
                "penetration": 0.10,
            },
            "Jungle": {
                "physical_power": 0.25 if damage_type == "Physical" else 0.05,
                "magical_power": 0.25 if damage_type == "Magical" else 0.05,
                "movement_speed": 0.20,
                "penetration": 0.20,
                "cooldown_reduction": 0.15,
                "physical_protection": 0.08,
                "magical_protection": 0.07,
            },
        }

        weights = role_stat_weights.get(role, role_stat_weights["Mid"])

        # Calculate stat-based fitness
        stat_score = 0.0
        for stat, weight in weights.items():
            stat_value = stats.get(stat, 0)
            if stat_value > 0:
                # Normalize stat values (rough normalization based on typical ranges)
                normalized_value = min(1.0, stat_value / self._get_stat_normalization_factor(stat))
                stat_score += normalized_value * weight

        # Category and tag bonuses
        category_score = self._get_category_role_bonus(category, role)
        tag_score = self._get_tag_role_bonus(tags, role)

        # Combined score
        total_score = (stat_score * 0.7) + (category_score * 0.2) + (tag_score * 0.1)

        return min(1.0, total_score)

    def _get_stat_normalization_factor(self, stat: str) -> float:
        """Get normalization factors for different stats."""
        normalization_factors = {
            "physical_power": 80,
            "magical_power": 120,
            "physical_protection": 80,
            "magical_protection": 80,
            "health": 400,
            "mana": 400,
            "attack_speed": 40,
            "critical_chance": 25,
            "lifesteal": 25,
            "penetration": 30,
            "movement_speed": 20,
            "cooldown_reduction": 20,
            "mp5": 15,
        }
        return normalization_factors.get(stat, 100)

    def _get_category_role_bonus(self, category: str, role: str) -> float:
        """Calculate category bonus for specific roles."""
        category_role_matrix = {
            "Defense": {"Solo": 0.9, "Support": 1.0, "Mid": 0.3, "Carry": 0.2, "Jungle": 0.4},
            "Physical": {"Solo": 0.6, "Support": 0.3, "Mid": 0.7, "Carry": 1.0, "Jungle": 0.9},
            "Magical": {"Solo": 0.4, "Support": 0.4, "Mid": 1.0, "Carry": 0.1, "Jungle": 0.7},
            "Starter": {"Solo": 0.8, "Support": 0.8, "Mid": 0.8, "Carry": 0.8, "Jungle": 0.8},
        }
        return category_role_matrix.get(category, {}).get(role, 0.5)

    def _get_tag_role_bonus(self, tags: List[str], role: str) -> float:
        """Calculate tag-based bonus for roles."""
        tag_role_bonuses = {
            "Solo": {"Defense": 0.3, "Health": 0.2, "Physical": 0.1},
            "Support": {"Defense": 0.3, "Support": 0.4, "Aura": 0.3},
            "Mid": {"Magical": 0.3, "Penetration": 0.2, "Power": 0.2, "Mana": 0.1},
            "Carry": {"Physical": 0.3, "Attack Speed": 0.2, "Lifesteal": 0.2},
            "Jungle": {"Physical": 0.2, "Magical": 0.2, "Mobility": 0.3},
        }

        role_bonuses = tag_role_bonuses.get(role, {})
        bonus = sum(role_bonuses.get(tag, 0) for tag in tags)
        return min(0.5, bonus)  # Cap at 0.5

    def _select_core_items(
        self, item_scores: List[tuple], role: str, damage_type: str, count: int
    ) -> List[Dict[str, Any]]:
        """Select core items that are essential for the role."""
        core_items: List[Dict[str, Any]] = []

        # Role-specific core requirements
        core_requirements = {
            "Solo": ["Defense", "Health"],
            "Support": ["Defense", "Support", "Aura"],
            "Mid": ["Magical" if damage_type == "Magical" else "Physical", "Power"],
            "Carry": ["Physical", "Attack Speed"],
            "Jungle": ["Physical" if damage_type == "Physical" else "Magical", "Mobility"],
        }

        requirements = core_requirements.get(role, [])

        for item, score in item_scores:
            if len(core_items) >= count:
                break

            # Check if item meets core requirements
            item_tags = item.get("tags", [])
            item_category = item.get("category", "")

            if any(req in item_tags or req in item_category for req in requirements):
                core_items.append(item)

        return core_items

    def _select_complementary_items(
        self, item_scores: List[tuple], role: str, existing_items: List[Dict[str, Any]], count: int
    ) -> List[Dict[str, Any]]:
        """Select items that complement the existing build."""
        complement_items: List[Dict[str, Any]] = []
        existing_categories = [item.get("category", "") for item in existing_items]

        # Avoid over-stacking same categories
        for item, score in item_scores:
            if len(complement_items) >= count:
                break

            if item in existing_items:
                continue

            item_category = item.get("category", "")

            # Limit items per category to ensure diversity
            if existing_categories.count(item_category) < 2:  # Max 2 items per category
                complement_items.append(item)
                existing_categories.append(item_category)

        return complement_items

    def _select_synergy_items(
        self, item_scores: List[tuple], existing_items: List[Dict[str, Any]], count: int
    ) -> List[Dict[str, Any]]:
        """Select items that have synergy with existing build."""
        synergy_items: List[Dict[str, Any]] = []
        existing_names = [item["name"] for item in existing_items]

        for item, score in item_scores:
            if len(synergy_items) >= count:
                break

            if item in existing_items:
                continue

            # Check for known synergies
            item_name = item["name"]
            has_synergy = False

            for synergy in self.item_synergies:
                if (synergy.item1 == item_name and synergy.item2 in existing_names) or (
                    synergy.item2 == item_name and synergy.item1 in existing_names
                ):
                    has_synergy = True
                    break

            if has_synergy or score > 0.7:  # High scoring items or synergistic items
                synergy_items.append(item)

        return synergy_items

    def _calculate_stat_efficiency(self, item: Dict[str, Any], role: str) -> float:
        """Calculate statistical efficiency of item stats for the role."""
        stats = item.get("stats", {})
        cost = item.get("cost", 1)

        if cost == 0:
            return 0.5  # Avoid division by zero

        # Calculate total stat value weighted by role importance
        role_weights = {
            "Solo": {
                "physical_protection": 15,
                "magical_protection": 15,
                "health": 2,
                "physical_power": 10,
            },
            "Support": {
                "physical_protection": 15,
                "magical_protection": 15,
                "health": 2,
                "mana": 1.5,
            },
            "Mid": {"magical_power": 8, "physical_power": 8, "penetration": 20, "mana": 1.5},
            "Carry": {"physical_power": 8, "attack_speed": 12, "critical_chance": 25},
            "Jungle": {
                "physical_power": 8,
                "magical_power": 8,
                "movement_speed": 15,
                "penetration": 20,
            },
        }

        weights = role_weights.get(role, role_weights["Mid"])

        total_value = 0
        for stat, value in stats.items():
            weight = weights.get(stat, 5)  # Default weight
            total_value += value * weight

        # Efficiency = value per gold spent
        efficiency = total_value / cost

        # Normalize to 0-1 range (based on typical efficiency ranges)
        normalized_efficiency = min(1.0, efficiency / 0.8)

        return normalized_efficiency

    def _calculate_cost_efficiency(self, item: Dict[str, Any], role: str) -> float:
        """Calculate cost efficiency relative to role needs."""
        cost = item.get("cost", 1)
        tier = item.get("tier", 1)

        # Cost efficiency based on tier and cost
        if tier == 1:  # Starter items
            return 0.8 if cost <= 1000 else 0.6
        elif tier == 2:  # Mid-tier items
            return 0.7 if cost <= 1800 else 0.5
        else:  # High-tier items
            return 0.9 if cost <= 2500 else 0.6

    def _calculate_synergy_potential(self, item: Dict[str, Any], role: str) -> float:
        """Calculate item's potential for synergies."""
        item_name = item["name"]
        synergy_count = 0
        synergy_strength = 0.0

        for synergy in self.item_synergies:
            if synergy.item1 == item_name or synergy.item2 == item_name:
                synergy_count += 1
                synergy_strength += synergy.synergy_score

        if synergy_count == 0:
            return 0.3  # Base potential for items with no defined synergies

        avg_synergy = synergy_strength / synergy_count
        return min(1.0, avg_synergy * (synergy_count / 5))  # Scale by number of synergies

    def _calculate_category_bonus(self, item: Dict[str, Any], role: str) -> float:
        """Calculate bonus based on item category appropriateness."""
        category = item.get("category", "")

        category_bonuses = {
            "Solo": {"Defense": 0.5, "Physical": 0.3, "Magical": 0.2},
            "Support": {"Defense": 0.6, "Starter": 0.2},
            "Mid": {"Magical": 0.5, "Physical": 0.5},
            "Carry": {"Physical": 0.6},
            "Jungle": {"Physical": 0.4, "Magical": 0.4, "Defense": 0.2},
        }

        return category_bonuses.get(role, {}).get(category, 0.1)

    def _calculate_class_synergy(
        self, item: Dict[str, Any], god_class: str, damage_type: str
    ) -> float:
        """Calculate synergy between item and god class."""
        stats = item.get("stats", {})
        category = item.get("category", "")

        # Class-specific synergy bonuses
        class_bonuses = {
            "Warrior": {"physical_power": 0.3, "physical_protection": 0.4, "health": 0.3},
            "Guardian": {"physical_protection": 0.4, "magical_protection": 0.4, "health": 0.2},
            "Mage": {"magical_power": 0.5, "mana": 0.3, "cooldown_reduction": 0.2},
            "Hunter": {"physical_power": 0.4, "attack_speed": 0.3, "critical_chance": 0.3},
            "Assassin": {"physical_power": 0.4, "movement_speed": 0.3, "penetration": 0.3},
        }

        bonuses = class_bonuses.get(god_class, {})
        synergy_score = 0.0

        for stat, bonus in bonuses.items():
            if stats.get(stat, 0) > 0:
                synergy_score += bonus

        # Damage type consistency bonus
        if (damage_type == "Physical" and category == "Physical") or (
            damage_type == "Magical" and category == "Magical"
        ):
            synergy_score += 0.2

        return min(1.0, synergy_score)

    def _optimize_for_playstyles(
        self, items: List[Dict[str, Any]], playstyles: List[str]
    ) -> List[Dict[str, Any]]:
        """Optimize build by replacing items that don't match playstyles."""
        if not playstyles:
            return items

        all_items = self.db.get_all_items()
        optimized_items = items.copy()

        # Score all items for playstyles
        item_scores = []
        for item in all_items:
            score = self._score_item_for_playstyles(item, playstyles)
            meta_score = self.meta_tiers.get(item["name"], 50)
            combined_score = score * (meta_score / 100)  # Normalize meta score
            item_scores.append((item, combined_score))

        # Sort items by combined score
        item_scores.sort(key=lambda x: x[1], reverse=True)

        # Replace lowest scoring items with better playstyle matches
        for i, current_item in enumerate(optimized_items):
            current_score = self._score_item_for_playstyles(current_item, playstyles)

            # If current item scores poorly for selected playstyles
            if current_score < 1.0:
                # Find a better replacement
                for replacement_item, replacement_score in item_scores:
                    if (
                        replacement_item not in optimized_items
                        and replacement_score > current_score * 1.5
                    ):  # Significantly better
                        optimized_items[i] = replacement_item
                        break

        return optimized_items

    def _apply_enemy_counters(
        self, items: List[Dict[str, Any]], enemy_comp: List[str]
    ) -> List[Dict[str, Any]]:
        """Apply intelligent enemy composition counters."""
        all_items = self.db.get_all_items()
        counter_items = []

        # Analyze enemy composition threats
        enemy_analysis = self._analyze_enemy_composition(enemy_comp)

        # Generate counter items based on threats
        if enemy_analysis["high_burst"]:
            counter_items.extend(["Magi's Cloak", "Spirit Robe", "Mantle of Discord"])

        if enemy_analysis["high_heal"]:
            counter_items.extend(["Divine Ruin", "Brawler's Beat Stick", "Pestilence"])

        if enemy_analysis["high_mobility"]:
            counter_items.extend(["Midgardian Mail", "Witchblade", "Frostbound Hammer"])

        if enemy_analysis["crit_heavy"]:
            counter_items.extend(["Spectral Armor", "Thorns", "Nemean Lion"])

        # Replace least optimal items with counters
        if counter_items:
            for counter_name in counter_items[:2]:  # Max 2 counter items
                counter_item = next((i for i in all_items if i["name"] == counter_name), None)
                if counter_item and len(items) > 0:
                    # Replace lowest meta rated item
                    lowest_item = min(items, key=lambda x: self.meta_tiers.get(x["name"], 50))
                    items[items.index(lowest_item)] = counter_item

        return items

    def _analyze_enemy_composition(self, enemy_comp: List[str]) -> Dict[str, bool]:
        """Analyze enemy composition for threat patterns."""
        analysis = {
            "high_burst": False,
            "high_heal": False,
            "high_mobility": False,
            "crit_heavy": False,
            "physical_heavy": False,
            "magical_heavy": False,
        }

        burst_gods = ["Zeus", "Scylla", "Vulcan", "Thor", "Loki", "Bastet"]
        heal_gods = ["Hel", "Aphrodite", "Ra", "Chang'e", "Guan Yu"]
        mobile_gods = ["Mercury", "Loki", "Serqet", "Ratatoskr", "Awilix"]
        crit_gods = ["Artemis", "Jing Wei", "Cernunnos", "Rama"]

        physical_count = 0
        magical_count = 0

        for enemy in enemy_comp:
            enemy_god = self.db.get_god(enemy)
            if enemy_god:
                if enemy_god.get("damage_type") == "Physical":
                    physical_count += 1
                else:
                    magical_count += 1

            if enemy in burst_gods:
                analysis["high_burst"] = True
            if enemy in heal_gods:
                analysis["high_heal"] = True
            if enemy in mobile_gods:
                analysis["high_mobility"] = True
            if enemy in crit_gods:
                analysis["crit_heavy"] = True

        analysis["physical_heavy"] = physical_count > magical_count
        analysis["magical_heavy"] = magical_count > physical_count

        return analysis

    def _enhance_with_synergies(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance build by maximizing item synergies."""
        item_names = [item["name"] for item in items]

        # Find best synergy opportunities
        synergy_scores = {}
        for synergy in self.item_synergies:
            if synergy.item1 in item_names and synergy.item2 in item_names:
                synergy_scores[f"{synergy.item1}+{synergy.item2}"] = synergy.synergy_score

        # If we have low synergy, try to improve
        if len(synergy_scores) < 2:
            all_items = self.db.get_all_items()
            # Try to add synergistic items
            for synergy in sorted(self.item_synergies, key=lambda x: x.synergy_score, reverse=True):
                if synergy.item1 in item_names:
                    # Try to add synergy.item2
                    synergy_item = next((i for i in all_items if i["name"] == synergy.item2), None)
                    if synergy_item and synergy_item not in items:
                        # Replace lowest impact item
                        items[-1] = synergy_item
                        break

        return items

    def _analyze_build_comprehensive(
        self, items: List[Dict[str, Any]], role: str, god: Dict[str, Any]
    ) -> BuildAnalysis:
        """Generate comprehensive build analysis."""

        # Calculate damage potential
        total_power = sum(
            item.get("stats", {}).get("physical_power", 0)
            + item.get("stats", {}).get("magical_power", 0)
            for item in items
        )
        damage_potential = min(100, (total_power / 400) * 100)  # Scale to 100

        # Calculate survivability
        total_health = sum(item.get("stats", {}).get("health", 0) for item in items)
        total_protections = sum(
            item.get("stats", {}).get("physical_protection", 0)
            + item.get("stats", {}).get("magical_protection", 0)
            for item in items
        )
        survivability = min(100, ((total_health / 1000) + (total_protections / 200)) * 50)

        # Calculate utility score
        utility_items = sum(
            1
            for item in items
            if any(util in item["name"].lower() for util in ["relic", "winged", "magi", "spirit"])
        )
        utility_score = min(100, (utility_items / 6) * 100)

        # Meta rating
        meta_rating = sum(self.meta_tiers.get(item["name"], 50) for item in items) / len(items)

        # Find power spikes
        power_spikes = self._identify_power_spikes(items)

        # Find synergies
        synergies = self._find_active_synergies(items)

        # Game phase ratings
        game_phase_rating = {
            "Early": min(100, 100 - (sum(item.get("cost", 0) for item in items[:2]) / 5000 * 100)),
            "Mid": min(100, (damage_potential + survivability) / 2),
            "Late": min(100, (meta_rating + utility_score) / 2),
        }

        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []

        if damage_potential > 75:
            strengths.append("High damage output")
        elif damage_potential < 40:
            weaknesses.append("Low damage potential")

        if survivability > 70:
            strengths.append("Excellent survivability")
        elif survivability < 30:
            weaknesses.append("Fragile build")

        if len(synergies) >= 2:
            strengths.append("Strong item synergies")
        elif len(synergies) == 0:
            weaknesses.append("Lacks item synergies")

        return BuildAnalysis(
            total_cost=sum(item.get("cost", 0) for item in items),
            damage_potential=damage_potential,
            survivability=survivability,
            utility_score=utility_score,
            meta_rating=meta_rating,
            power_spikes=power_spikes,
            synergies=synergies,
            weaknesses=weaknesses,
            strengths=strengths,
            game_phase_rating=game_phase_rating,
        )

    def _identify_power_spikes(self, items: List[Dict[str, Any]]) -> List[PowerSpike]:
        """Identify power spikes in the build progression."""
        spikes = []
        cumulative_cost = 0

        for i, item in enumerate(items):
            cumulative_cost += item.get("cost", 0)
            item_name = item["name"]

            # High impact items create power spikes
            if self.meta_tiers.get(item_name, 50) > 80:
                if cumulative_cost < 5000:
                    spike_type = "Early"
                elif cumulative_cost < 10000:
                    spike_type = "Mid"
                else:
                    spike_type = "Late"

                power_rating = self.meta_tiers.get(item_name, 50)
                description = f"{item_name} provides significant {spike_type.lower()} game impact"

                spikes.append(PowerSpike(i, item_name, spike_type, power_rating, description))

        return spikes

    def _find_active_synergies(self, items: List[Dict[str, Any]]) -> List[ItemSynergy]:
        """Find active synergies in the current build."""
        item_names = [item["name"] for item in items]
        active_synergies = []

        for synergy in self.item_synergies:
            if synergy.item1 in item_names and synergy.item2 in item_names:
                active_synergies.append(synergy)

        return active_synergies

    def _generate_build_order(self, items: List[Dict[str, Any]], role: str) -> List[Dict[str, Any]]:
        """Generate optimal item purchase order with sophisticated priority logic."""
        if not items:
            return []

        # Enhanced item priority system
        item_priorities = []

        for item in items:
            priority_data = self._calculate_item_priority(item, role, items)
            item_priorities.append(
                {
                    "item": item,
                    "priority_score": priority_data["total_score"],
                    "early_game_value": priority_data["early_value"],
                    "cost_efficiency": priority_data["cost_efficiency"],
                    "power_spike_tier": priority_data["power_spike"],
                    "role_fit": priority_data["role_fit"],
                    "recommended_timing": priority_data["timing"],
                }
            )

        # Sort by multiple factors with intelligent ordering
        ordered_priorities = self._intelligent_item_ordering(item_priorities, role)

        # Generate detailed build order with reasoning
        build_order = []
        cumulative_cost = 0

        for i, priority_item in enumerate(ordered_priorities):
            item = priority_item["item"]
            cumulative_cost += item.get("cost", 0)

            # Determine purchase reasoning
            reason = self._get_purchase_reasoning(priority_item, i + 1, cumulative_cost)

            build_order.append(
                {
                    "order": i + 1,
                    "item": item["name"],
                    "cost": item.get("cost", 0),
                    "cumulative_cost": cumulative_cost,
                    "timing": priority_item["recommended_timing"],
                    "reason": reason,
                    "priority_score": round(priority_item["priority_score"], 1),
                    "cost_efficiency": round(priority_item["cost_efficiency"], 1),
                }
            )

        return build_order

    def _calculate_item_priority(
        self, item: Dict[str, Any], role: str, all_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive item priority score."""
        item_name = item["name"]
        item_cost = item.get("cost", 0)
        item_stats = item.get("stats", {})

        # Base meta score
        meta_score = self.meta_tiers.get(item_name, 50)

        # Cost efficiency calculation (impact per gold)
        if item_cost > 0:
            # Factor in both meta rating and stat values
            stats_value = sum(v for v in item_stats.values() if isinstance(v, (int, float)))
            cost_efficiency = (meta_score + stats_value * 0.1) / (item_cost / 1000)
        else:
            cost_efficiency = 0

        # Early game value (cheaper items have higher early value)
        if item_cost <= 1500:
            early_value = 100
        elif item_cost <= 2500:
            early_value = 80
        elif item_cost <= 3500:
            early_value = 60
        else:
            early_value = 40

        # Power spike determination
        power_spike_score = 0
        if meta_score >= 90:
            power_spike_score = 100  # S+ tier
        elif meta_score >= 85:
            power_spike_score = 85  # S tier
        elif meta_score >= 75:
            power_spike_score = 70  # A tier
        else:
            power_spike_score = 50  # B/C tier

        # Role fit scoring
        role_fit = self._calculate_role_fit(item, role)

        # Game timing recommendation
        if item_cost <= 2000:
            timing = "Early Game (0-10 min)"
        elif item_cost <= 3500:
            timing = "Mid Game (10-20 min)"
        else:
            timing = "Late Game (20+ min)"

        # Total priority score with intelligent weighting
        role_priorities = self.role_priorities.get(
            role, {"damage": 0.5, "survivability": 0.3, "utility": 0.2}
        )

        total_score = (
            meta_score * 0.3  # Meta viability
            + cost_efficiency * 0.25  # Gold efficiency
            + early_value * 0.2  # Early impact
            + power_spike_score * 0.15  # Power spike potential
            + role_fit * 0.1  # Role synergy
        )

        return {
            "total_score": total_score,
            "early_value": early_value,
            "cost_efficiency": cost_efficiency,
            "power_spike": power_spike_score,
            "role_fit": role_fit,
            "timing": timing,
        }

    def _calculate_role_fit(self, item: Dict[str, Any], role: str) -> float:
        """Calculate how well an item fits the role."""
        item_name = item["name"].lower()
        item_stats = item.get("stats", {})

        role_item_keywords = {
            "Solo": ["protection", "health", "defense", "breastplate", "hide", "spirit"],
            "Support": ["aura", "sovereignty", "heartward", "thebes", "relic", "team"],
            "Mid": ["power", "rod", "book", "staff", "magical", "penetration"],
            "Carry": ["physical", "attack", "critical", "bow", "qin", "executioner"],
            "Jungle": ["movement", "speed", "jotunn", "heartseeker", "mobility"],
        }

        role_stat_priorities = {
            "Solo": ["physical_protection", "magical_protection", "health"],
            "Support": ["physical_protection", "magical_protection", "health", "mp5"],
            "Mid": ["magical_power", "magical_penetration", "cooldown_reduction"],
            "Carry": ["physical_power", "attack_speed", "critical_chance"],
            "Jungle": ["physical_power", "movement_speed", "penetration"],
        }

        # Keyword matching
        keywords = role_item_keywords.get(role, [])
        keyword_score = sum(10 for keyword in keywords if keyword in item_name)

        # Stat matching
        priority_stats = role_stat_priorities.get(role, [])
        stat_score = sum(
            5 for stat in priority_stats if stat in item_stats and item_stats[stat] > 0
        )

        return min(100, keyword_score + stat_score)

    def _intelligent_item_ordering(
        self, item_priorities: List[Dict[str, Any]], role: str
    ) -> List[Dict[str, Any]]:
        """Intelligently order items considering multiple factors."""

        # Separate items by cost tiers for smart ordering
        early_items = [p for p in item_priorities if p["item"].get("cost", 0) <= 2000]
        mid_items = [p for p in item_priorities if 2000 < p["item"].get("cost", 0) <= 3500]
        late_items = [p for p in item_priorities if p["item"].get("cost", 0) > 3500]

        # Sort each tier by appropriate criteria
        # Early: prioritize cost efficiency and early value
        early_items.sort(key=lambda x: x["cost_efficiency"] + x["early_game_value"], reverse=True)

        # Mid: prioritize power spikes and role fit
        mid_items.sort(key=lambda x: x["power_spike_tier"] + x["role_fit"], reverse=True)

        # Late: prioritize overall power and meta score
        late_items.sort(key=lambda x: x["priority_score"], reverse=True)

        # Role-specific ordering adjustments
        if role == "Support":
            # Supports need early utility and team items
            return self._prioritize_support_items(early_items, mid_items, late_items)
        elif role == "Carry":
            # Carries need damage progression
            return self._prioritize_carry_items(early_items, mid_items, late_items)
        elif role == "Solo":
            # Solo needs early defense, then damage
            return self._prioritize_solo_items(early_items, mid_items, late_items)
        else:
            # Standard ordering for Mid/Jungle
            return early_items + mid_items + late_items

    def _prioritize_support_items(self, early: List, mid: List, late: List) -> List:
        """Support-specific item ordering."""
        # Supports prioritize: Early utility -> Team items -> Late game utility
        aura_items = [
            item
            for item in early + mid + late
            if any(
                keyword in item["item"]["name"].lower()
                for keyword in ["sovereignty", "heartward", "thebes", "aura"]
            )
        ]
        other_items = [item for item in early + mid + late if item not in aura_items]

        return aura_items + other_items

    def _prioritize_carry_items(self, early: List, mid: List, late: List) -> List:
        """Carry-specific item ordering."""
        # Carries prioritize: Lifesteal -> Attack speed -> Crit -> Penetration
        lifesteal_items = [
            item for item in early + mid if "lifesteal" in item["item"].get("stats", {})
        ]
        crit_items = [
            item
            for item in mid + late
            if any(
                keyword in item["item"]["name"].lower()
                for keyword in ["deathbringer", "rage", "crit"]
            )
        ]
        other_items = [
            item
            for item in early + mid + late
            if item not in lifesteal_items and item not in crit_items
        ]

        return lifesteal_items + other_items + crit_items

    def _prioritize_solo_items(self, early: List, mid: List, late: List) -> List:
        """Solo-specific item ordering."""
        # Solo prioritizes: Early defense -> Damage/utility -> Late game power
        defense_items = [
            item
            for item in early + mid
            if any(
                keyword in item["item"]["name"].lower()
                for keyword in ["protection", "breastplate", "hide"]
            )
        ]
        other_items = [item for item in early + mid + late if item not in defense_items]

        return defense_items + other_items

    def _get_purchase_reasoning(
        self, priority_item: Dict[str, Any], order: int, cumulative_cost: int
    ) -> str:
        """Generate intelligent reasoning for item purchase order."""
        item = priority_item["item"]
        timing = priority_item["recommended_timing"]
        cost_eff = priority_item["cost_efficiency"]

        reasons = []

        if order == 1:
            if cost_eff > 80:
                reasons.append("Excellent early game value")
            else:
                reasons.append("Essential first item")
        elif order <= 3:
            if priority_item["power_spike_tier"] > 85:
                reasons.append("Major power spike item")
            elif priority_item["early_game_value"] > 80:
                reasons.append("Strong early-mid game impact")
            else:
                reasons.append("Core build item")
        else:
            if cumulative_cost > 12000:
                reasons.append("Late game scaling item")
            else:
                reasons.append("Mid-game optimization")

        # Add specific reasoning based on item characteristics
        item_name = item["name"].lower()
        if any(keyword in item_name for keyword in ["protection", "defense"]):
            reasons.append("defensive priority")
        elif any(keyword in item_name for keyword in ["power", "damage"]):
            reasons.append("damage scaling")
        elif any(keyword in item_name for keyword in ["heal", "lifesteal"]):
            reasons.append("sustain focus")

        return f"{timing} - {', '.join(reasons)}"

    def _generate_alternatives(
        self, items: List[Dict[str, Any]], enemy_comp: Optional[List[str]]
    ) -> Dict[str, List[str]]:
        """Generate situational item alternatives."""
        all_items = self.db.get_all_items()
        alternatives = {}

        for item in items:
            item_alternatives = []
            item_name = item["name"]

            # Find similar items (same category/function)
            for alt_item in all_items:
                if (
                    alt_item["name"] != item_name
                    and abs(
                        self.meta_tiers.get(alt_item["name"], 50)
                        - self.meta_tiers.get(item_name, 50)
                    )
                    < 20
                ):
                    item_alternatives.append(alt_item["name"])

            if item_alternatives:
                alternatives[item_name] = item_alternatives[:3]  # Top 3 alternatives

        return alternatives

    def _generate_counter_strategy(self, enemy_comp: List[str]) -> Dict[str, Any]:
        """Generate strategy for countering enemy composition."""
        enemy_analysis = self._analyze_enemy_composition(enemy_comp)

        strategies = []
        if enemy_analysis["high_burst"]:
            strategies.append("Build magic/physical defense early to survive burst")
        if enemy_analysis["high_heal"]:
            strategies.append("Prioritize anti-heal items to reduce enemy sustain")
        if enemy_analysis["high_mobility"]:
            strategies.append("Get movement speed reduction items to catch mobile targets")
        if enemy_analysis["crit_heavy"]:
            strategies.append("Build critical strike defense to reduce crit effectiveness")

        return {
            "primary_threats": enemy_comp,
            "threat_analysis": enemy_analysis,
            "recommended_strategies": strategies,
            "priority_targets": enemy_comp[:2],  # Focus first two enemies
        }

    def _calculate_meta_score(self, items: List[Dict[str, Any]]) -> float:
        """Calculate overall meta viability score."""
        if not items:
            return 0.0

        total_score = sum(self.meta_tiers.get(item["name"], 50) for item in items)
        return round(total_score / len(items), 1)

    def _generate_power_timeline(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate power progression timeline."""
        timeline = []
        cumulative_cost = 0
        cumulative_power = 0

        for i, item in enumerate(items):
            cumulative_cost += item.get("cost", 0)
            item_power = self.meta_tiers.get(item["name"], 50)
            cumulative_power += item_power

            timeline.append(
                {
                    "item_number": i + 1,
                    "item_name": item["name"],
                    "total_cost": cumulative_cost,
                    "power_level": round(cumulative_power / (i + 1), 1),
                    "game_stage": (
                        "Early"
                        if cumulative_cost < 5000
                        else "Mid" if cumulative_cost < 10000 else "Late"
                    ),
                }
            )

        return timeline

    def _optimize_for_phase(
        self, items: List[Dict[str, Any]], game_phase: str, budget: int
    ) -> List[Dict[str, Any]]:
        """Optimize build for specific game phase."""
        if game_phase == "Early":
            # Prioritize low-cost, high-impact items
            items.sort(key=lambda x: x.get("cost", 0))
        elif game_phase == "Late":
            # Prioritize high-cost, high-impact items
            items.sort(key=lambda x: self.meta_tiers.get(x["name"], 50), reverse=True)

        # Ensure build fits budget
        total_cost = sum(item.get("cost", 0) for item in items)
        while total_cost > budget and items:
            # Remove most expensive item
            most_expensive = max(items, key=lambda x: x.get("cost", 0))
            items.remove(most_expensive)
            total_cost = sum(item.get("cost", 0) for item in items)

        return items
