#!/usr/bin/env python3
"""🔥 PROFESSIONAL BUILD OPTIMIZER - ENHANCED WITH GOD ANALYSIS 🔥"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from advanced_god_analyzer import AdvancedGodAnalyzer
from database import Database


@dataclass
class ItemSynergy:
    """Represents synergy between two items."""

    item1: str
    item2: str
    synergy_score: float
    reason: str


@dataclass
class ProfessionalAnalysis:
    """Professional-grade build analysis."""

    damage_potential: float
    survivability: float
    utility_score: float
    meta_rating: float
    total_cost: int
    strengths: List[str]
    weaknesses: List[str]
    synergy_score: float
    meta_compliance: float
    damage_simulation: Dict[str, float]
    power_spikes: List[str]
    recommendation: str


class ProfessionalBuildOptimizer:
    """🔥 PROFESSIONAL Build Optimizer with Advanced God Analysis 🔥"""

    def __init__(self, db: Database):
        self.db = db
        self.god_analyzer = AdvancedGodAnalyzer(db)
        self._init_role_priorities()
        self._init_counter_build_rules()
        self._init_team_synergy_rules()

    def _init_role_priorities(self):
        """Enhanced role priorities with meta intelligence."""
        self.role_priorities = {
            "Mid": {
                "categories": ["Magical", "Physical"],
                "stat_weights": {
                    "magical_power": 4.0,
                    "physical_power": 4.0,
                    "penetration": 3.0,
                    "cooldown_reduction": 2.5,
                    "mana": 2.0,
                },
                "avoid_categories": ["Defense"],
                "meta_focus": "burst_damage",
            },
            "Solo": {
                "categories": ["Defense", "Physical", "Magical"],
                "stat_weights": {
                    "physical_protection": 4.0,
                    "magical_protection": 4.0,
                    "health": 3.5,
                    "cooldown_reduction": 3.0,
                    "physical_power": 2.0,
                    "magical_power": 2.0,
                },
                "avoid_categories": [],
                "meta_focus": "sustain_frontline",
            },
            "Support": {
                "categories": ["Defense", "Starter"],
                "stat_weights": {
                    "physical_protection": 4.5,
                    "magical_protection": 4.5,
                    "health": 4.0,
                    "cooldown_reduction": 3.0,
                    "mana": 2.0,
                },
                "avoid_categories": [],
                "meta_focus": "team_utility",
            },
            "Carry": {
                "categories": ["Physical"],
                "stat_weights": {
                    "physical_power": 4.0,
                    "attack_speed": 3.5,
                    "critical_chance": 3.0,
                    "lifesteal": 2.5,
                    "penetration": 2.0,
                },
                "avoid_categories": ["Magical", "Defense"],
                "meta_focus": "dps_scaling",
            },
            "Jungle": {
                "categories": ["Physical", "Magical"],
                "stat_weights": {
                    "physical_power": 3.5,
                    "magical_power": 3.5,
                    "penetration": 3.0,
                    "movement_speed": 2.5,
                    "cooldown_reduction": 2.0,
                },
                "avoid_categories": ["Defense"],
                "meta_focus": "burst_mobility",
            },
        }

    def _init_counter_build_rules(self):
        """🔥 BADASS Counter-Build Intelligence 🔥"""
        self.counter_rules = {
            # Anti-Physical
            "heavy_physical": {
                "items": ["Sovereignty", "Midgardian Mail", "Witchblade"],
                "trigger": "physical_damage_heavy",
            },
            # Anti-Magical
            "heavy_magical": {
                "items": ["Heartward Amulet", "Pestilence", "Runic Shield"],
                "trigger": "magical_damage_heavy",
            },
            # Anti-Healing
            "heavy_healing": {
                "items": ["Divine Ruin", "Brawler's Beat Stick", "Pestilence"],
                "trigger": "healing_comp",
            },
            # Anti-Crit
            "crit_heavy": {"items": ["Spectral Armor"], "trigger": "crit_based_carry"},
        }

    def _init_team_synergy_rules(self):
        """Team composition synergy analysis."""
        self.team_synergies = {
            "engage_comp": ["Blink Rune", "Shell", "Sprint"],
            "poke_comp": ["Penetration", "Cooldown Reduction"],
            "sustain_comp": ["Lifesteal", "Health", "Protections"],
            "burst_comp": ["Power", "Penetration", "Cooldown Reduction"],
        }

    def _ensure_item_dict(self, item):
        """Ensure item is a dict with at least a 'name' key."""
        if isinstance(item, dict):
            if "name" in item:
                return item
            elif "item_name" in item:
                # Convert API-style dict to internal format
                new_item = item.copy()
                new_item["name"] = new_item.pop("item_name")
                return new_item
            else:
                # Fallback: treat as string
                return {"name": str(item)}
        else:
            return {"name": str(item)}

    def optimize_build(
        self,
        god_name: str,
        role: str,
        enemy_comp: Optional[List[str]] = None,
        game_phase: str = "All",
        budget: int = 15000,
        playstyles: Optional[List[str]] = None,
        team_comp: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """🔥 PROFESSIONAL Build Optimization with Advanced Analytics 🔥"""
        try:
            # 🐛 DEBUG: Log optimization request
            print(f"🔧 BUILD OPTIMIZATION REQUEST:")
            print(f"   God: {god_name}")
            print(f"   Role: {role}")
            print(f"   Enemy Comp: {enemy_comp}")
            print(f"   Budget: {budget}")

            # Get god information
            god = self.db.get_god(god_name)
            if not god:
                print(f"❌ God '{god_name}' not found in database")
                return {"error": f"God '{god_name}' not found"}

            print(f"✅ Found god: {god.get('name')} ({god.get('role')}, {god.get('damage_type')})")

            # Get all items
            all_items = self.db.get_all_items()
            if not all_items:
                print("❌ No items found in database")
                return {"error": "No items found in database"}

            # Defensive: ensure all items are dicts with 'name'
            all_items = [self._ensure_item_dict(item) for item in all_items]

            print(f"✅ Found {len(all_items)} items in database")

            # 🔥 PROFESSIONAL ANALYSIS PIPELINE 🔥

            # 1. Get meta template from god analyzer
            meta_template = self.god_analyzer.get_meta_template(god_name, role)
            print(f"📊 Meta template: {meta_template.god_name if meta_template else 'None'}")

            # 2. Score items using advanced synergy calculation
            scored_items = self._score_items_with_god_analysis(
                all_items, god_name, role, enemy_comp, team_comp
            )

            print(f"🧮 Scored {len(scored_items)} items, top 5 scores:")
            for item, score in sorted(scored_items, key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {item.get('name', 'Unknown')}: {score:.2f}")

            # 3. Apply counter-build adjustments
            if enemy_comp:
                scored_items = self._apply_counter_build_logic(scored_items, enemy_comp)
                print(f"🛡️ Applied counter-build logic for: {enemy_comp}")

            # 4. Apply team synergy bonuses
            if team_comp:
                scored_items = self._apply_team_synergy_bonuses(scored_items, team_comp)
                print(f"🤝 Applied team synergy for: {team_comp}")

            # 5. Select optimal items with variety
            sorted_items = sorted(scored_items, key=lambda x: x[1], reverse=True)
            selected_items = self._select_diverse_items(sorted_items, 6)

            print(f"🎯 Selected items: {[item.get('name') for item in selected_items]}")

            # 6. 🔥 COMPREHENSIVE ANALYSIS 🔥
            analysis = self._generate_professional_analysis(
                selected_items, god_name, role, meta_template
            )

            # 7. Calculate build metrics
            total_cost = sum(item.get("cost", 0) for item in selected_items)

            result = {
                "items": [
                    {
                        "item_name": item.get("name"),
                        "category": item.get("category"),
                        "tags": item.get("tags"),
                        "cost": item.get("cost"),
                    }
                    for item in selected_items
                ],
                "build_order": self._optimize_build_order(selected_items, god_name),
                "total_cost": total_cost,
                "analysis": analysis,
                "meta_score": analysis.meta_compliance,
                "synergy_score": analysis.synergy_score,
                "damage_simulation": analysis.damage_simulation,
                "power_spikes": analysis.power_spikes,
                "alternatives": self._generate_alternatives(sorted_items[6:12]),
                "counters": self._analyze_counters(selected_items, enemy_comp),
                "build_explanation": analysis.recommendation,
                "optimization_details": {
                    "candidates_tested": len(all_items),
                    "optimization_strategy": "Advanced God Analysis + Meta Intelligence",
                    "role_focus": role,
                    "god_compatibility": analysis.synergy_score,
                    "meta_template_used": meta_template.god_name if meta_template else None,
                    "counter_adjustments": len(enemy_comp) if enemy_comp else 0,
                },
            }

            print(f"✅ Build optimization complete!")
            print(f"   Total Cost: {total_cost:,}g")
            print(f"   Meta Score: {analysis.meta_compliance:.2f}")
            print(f"   Synergy Score: {analysis.synergy_score:.2f}")

            return result

        except Exception as e:
            print(f"❌ Professional optimization failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return {"error": f"Professional optimization failed: {str(e)}"}

    def _score_items_with_god_analysis(
        self,
        items: List[Dict[str, Any]],
        god_name: str,
        role: str,
        enemy_comp: Optional[List[str]] = None,
        team_comp: Optional[List[str]] = None,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Score items using advanced god analysis."""
        scored_items: List[Tuple[Dict[str, Any], float]] = []
        role_priorities = self.role_priorities.get(role, self.role_priorities["Mid"])

        # Get god info for damage type filtering
        god = self.db.get_god(god_name)
        god_damage_type = god.get("damage_type", "Magical") if god else "Magical"

        # DEBUG: Log god data
        with open("scaling_debug.log", "a", encoding="utf-8") as f:
            f.write(f"[DEBUG] Scoring items for god: {god_name}\n")
            f.write(f"[DEBUG] God data: {god}\n")
            f.write(f"[DEBUG] God damage_type: {god_damage_type}\n")
            f.write(f"[DEBUG] God stats: {god.get('stats', {}) if god else {}}\n")
            f.write(
                f"[DEBUG] God intelligence: {god.get('intelligence', 'None') if god else 'None'}\n"
            )
            f.write(f"[DEBUG] God strength: {god.get('strength', 'None') if god else 'None'}\n")
            f.write("-" * 50 + "\n")

        for item in items:
            if not item or "name" not in item:
                continue

            # 🔥 FILTER OUT INAPPROPRIATE ITEMS 🔥
            item_category = item.get("category", "")
            item_tags = item.get("tags", [])

            # DEBUG: Log the first few items to see their categories
            if len(scored_items) < 5:
                print(
                    f"[DEBUG] Item: {item.get('name', 'Unknown')} | Category: {item_category} | Tags: {item_tags}"
                )

            # Skip relics and consumables for main builds
            if item_category in ["Relic", "Consumable"]:
                print(f"[DEBUG] Skipping {item.get('name', 'Unknown')} - category: {item_category}")
                continue

            # Skip starter items for main builds (unless it's a starter-focused role)
            if item_category == "Starter" and role not in ["Support"]:
                print(f"[DEBUG] Skipping {item.get('name', 'Unknown')} - starter item")
                continue

            # Filter by damage type compatibility
            if god_damage_type == "Magical":
                # For magical gods, prefer magical items, avoid physical-only items
                if "Physical" in item_tags and "Magical" not in item_tags:
                    print(
                        f"[DEBUG] Skipping {item.get('name', 'Unknown')} - physical-only for magical god"
                    )
                    continue  # Skip physical-only items for magical gods
            elif god_damage_type == "Physical":
                # For physical gods, prefer physical items, avoid magical-only items
                if "Magical" in item_tags and "Physical" not in item_tags:
                    print(
                        f"[DEBUG] Skipping {item.get('name', 'Unknown')} - magical-only for physical god"
                    )
                    continue  # Skip magical-only items for physical gods

            # Base role scoring
            base_score = self._calculate_base_role_score(item, role_priorities, god_name)

            # 🔥 ADVANCED GOD SYNERGY 🔥
            try:
                synergy = self.god_analyzer.calculate_item_synergy(god_name, item, role)
                synergy_score = synergy.total_synergy * 2.0  # Amplify synergy importance
            except Exception as e:
                print(
                    f"[WARNING] Synergy calculation failed for {item.get('name', 'Unknown')}: {e}"
                )
                synergy_score = 0.5  # Default synergy score

            # Meta template bonus
            meta_template = self.god_analyzer.get_meta_template(god_name, role)
            meta_bonus = 0.0
            if meta_template and item["name"] in meta_template.core_items:
                meta_bonus = 3.0  # Increased bonus for core items
            elif meta_template and item["name"] in meta_template.situational_items:
                meta_bonus = 1.5  # Increased bonus for situational items

            # Role-specific bonuses
            role_bonus = 0.0
            if role == "Mid" and item_category in ["Magical", "Offensive"]:
                role_bonus = 1.0
            elif role == "Carry" and item_category in ["Physical", "Offensive"]:
                role_bonus = 1.0
            elif role == "Solo" and item_category in ["Defense", "Hybrid"]:
                role_bonus = 1.0
            elif role == "Support" and item_category in ["Defense", "Starter"]:
                role_bonus = 1.0
            elif role == "Jungle" and item_category in ["Physical", "Magical", "Offensive"]:
                role_bonus = 1.0

            # Cost efficiency bonus
            cost_efficiency = self._calculate_item_efficiency(item)
            efficiency_bonus = min(cost_efficiency * 0.5, 1.0)

            # Combine scores with better weighting
            total_score = (
                base_score * 0.3
                + synergy_score * 0.3
                + meta_bonus * 0.2
                + role_bonus * 0.1
                + efficiency_bonus * 0.1
            )

            scored_items.append((item, total_score))

        return scored_items

    def _calculate_base_role_score(
        self, item: Dict[str, Any], role_priorities: Dict[str, Any], god_name: str
    ) -> float:
        """Calculate base role-specific score with real Smite 2 Intelligence/Strength scaling."""
        score = 0.0

        # Get god info for damage type and real scaling stats
        god = self.db.get_god(god_name)
        god_damage_type = god.get("damage_type", "Magical") if god else "Magical"
        god_stats = god.get("stats", {}) if god else {}

        # 🔥 REAL SMITE 2 SCALING DATA 🔥
        god_intelligence = god_stats.get("intelligence")
        god_strength = god_stats.get("strength")

        # DEBUG: Log scaling calculation for first few items
        if item.get("name", "").startswith(
            "A"
        ):  # Only log for items starting with 'A' to avoid spam
            with open("scaling_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[DEBUG] Scoring item: {item.get('name', 'Unknown')}\n")
                f.write(f"[DEBUG] God intelligence: {god_intelligence}, strength: {god_strength}\n")
                f.write(f"[DEBUG] Item stats: {item.get('stats', {})}\n")
                f.write(f"[DEBUG] Item tags: {item.get('tags', [])}\n")

        # Category scoring
        item_category = item.get("category", "")
        preferred_categories = role_priorities.get("categories", [])
        avoid_categories = role_priorities.get("avoid_categories", [])

        if item_category in avoid_categories:
            score -= 2.0  # Heavy penalty for avoided categories
        elif item_category in preferred_categories:
            score += 1.5  # Bonus for preferred categories

        # Damage type scoring
        item_tags = item.get("tags", [])
        if god_damage_type == "Magical" and "Magical" in item_tags:
            score += 2.0  # Strong bonus for matching damage type
        elif god_damage_type == "Physical" and "Physical" in item_tags:
            score += 2.0  # Strong bonus for matching damage type
        elif god_damage_type == "Magical" and "Physical" in item_tags:
            score -= 1.5  # Penalty for wrong damage type
        elif god_damage_type == "Physical" and "Magical" in item_tags:
            score -= 1.5  # Penalty for wrong damage type

        # 🔥 REAL INTELLIGENCE/STRENGTH SCALING BONUSES 🔥
        scaling_bonus = 0.0
        if god_intelligence is not None:
            # Intelligence affects magical power scaling
            if god_damage_type == "Magical":
                scaling_bonus += float(god_intelligence) * 0.3  # Bonus for high intelligence mages
            elif god_damage_type == "Physical":
                scaling_bonus += (
                    float(god_intelligence) * 0.1
                )  # Smaller bonus for physical gods with intelligence

        if god_strength is not None:
            # Strength affects physical power scaling
            if god_damage_type == "Physical":
                scaling_bonus += float(god_strength) * 0.3  # Bonus for high strength physical gods
            elif god_damage_type == "Magical":
                scaling_bonus += (
                    float(god_strength) * 0.1
                )  # Smaller bonus for magical gods with strength

        score += scaling_bonus

        # DEBUG: Log final score for first few items
        if item.get("name", "").startswith(
            "A"
        ):  # Only log for items starting with 'A' to avoid spam
            with open("scaling_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[DEBUG] Final score: {score:.2f} (scaling bonus: {scaling_bonus:.2f})\n")
                f.write("-" * 30 + "\n")

        # Stat scoring based on role
        item_stats = item.get("stats", {})

        if role_priorities.get("primary_stats"):
            for stat in role_priorities["primary_stats"]:
                if stat in item_stats:
                    score += item_stats[stat] * 0.1  # Bonus for primary stats

        if role_priorities.get("secondary_stats"):
            for stat in role_priorities["secondary_stats"]:
                if stat in item_stats:
                    score += item_stats[stat] * 0.05  # Smaller bonus for secondary stats

        return score

    def _apply_counter_build_logic(
        self, scored_items: List[Tuple[Dict[str, Any], float]], enemy_comp: List[str]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """🔥 Apply intelligent counter-building 🔥"""
        # Analyze enemy composition
        enemy_analysis = self._analyze_enemy_composition(enemy_comp)

        # Apply counter bonuses
        for i, (item, score) in enumerate(scored_items):
            item_name = item.get("name", "")

            # Check if item counters enemy composition
            for threat_type, counter_rule in self.counter_rules.items():
                if threat_type in enemy_analysis and item_name in counter_rule["items"]:
                    scored_items[i] = (item, score + 1.5)  # Counter bonus

        return scored_items

    def _analyze_enemy_composition(self, enemy_comp: List[str]) -> List[str]:
        """Analyze enemy composition for threats."""
        threats = []

        # Simple analysis (can be enhanced with god database)
        physical_count = sum(1 for god in enemy_comp if god in ["Apollo", "Artemis", "Achilles"])
        magical_count = sum(1 for god in enemy_comp if god in ["Agni", "Scylla", "Zeus"])

        if physical_count >= 3:
            threats.append("heavy_physical")
        if magical_count >= 3:
            threats.append("heavy_magical")

        # Check for specific threats
        healing_gods = ["Chang'e", "Hel", "Aphrodite", "Ra"]
        if any(god in enemy_comp for god in healing_gods):
            threats.append("heavy_healing")

        return threats

    def _apply_team_synergy_bonuses(
        self, scored_items: List[Tuple[Dict[str, Any], float]], team_comp: List[str]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Apply team composition synergy bonuses."""
        # Simple team analysis (can be enhanced)
        for i, (item, score) in enumerate(scored_items):
            # Aura items get bonus with team-focused gods
            if "aura" in item.get("tags", []) and len(team_comp) > 2:
                scored_items[i] = (item, score + 0.5)

        return scored_items

    def _generate_professional_analysis(
        self, items: List[Dict[str, Any]], god_name: str, role: str, meta_template
    ) -> ProfessionalAnalysis:
        """🔥 Generate comprehensive professional analysis 🔥"""
        # Use god analyzer for comprehensive analysis
        try:
            analysis_data = self.god_analyzer.analyze_build_effectiveness(god_name, role, items)
        except Exception as e:
            print(f"[WARNING] God analyzer failed: {e}")
            # Fallback analysis
            analysis_data = {
                "synergy_score": 0.6,
                "meta_compliance": 0.5,
                "damage_analysis": {
                    "dps": 500,
                    "ability_damage": 300,
                    "auto_attack_damage": 200,
                    "effective_health": 5000,
                },
                "recommendation": "Solid build with room for optimization",
            }

        # Calculate traditional metrics
        total_cost = sum(item.get("cost", 0) for item in items)

        # Calculate damage/survivability/utility
        damage_stats = [
            "physical_power",
            "magical_power",
            "attack_speed",
            "critical_chance",
            "penetration",
        ]
        defense_stats = ["physical_protection", "magical_protection", "health"]
        utility_stats = ["cooldown_reduction", "movement_speed", "mana"]

        damage_total = sum(
            sum(item.get("stats", {}).get(stat, 0) for stat in damage_stats) for item in items
        )
        defense_total = sum(
            sum(item.get("stats", {}).get(stat, 0) for stat in defense_stats) for item in items
        )
        utility_total = sum(
            sum(item.get("stats", {}).get(stat, 0) for stat in utility_stats) for item in items
        )

        damage_potential = min(1.0, damage_total / 400.0)
        survivability = min(1.0, defense_total / 500.0)
        utility_score = min(1.0, utility_total / 150.0)

        # Generate strengths and weaknesses based on analysis
        strengths = []
        weaknesses = []

        # Analyze build composition
        item_categories = [item.get("category", "Other") for item in items]
        category_counts: Dict[str, int] = {}
        for category in item_categories:
            category_counts[category] = category_counts.get(category, 0) + 1

        # Check for good category distribution
        if len(category_counts) >= 3:
            strengths.append("Well-rounded item selection")
        else:
            weaknesses.append("Limited item variety")

        # Check synergy
        if analysis_data["synergy_score"] > 0.7:
            strengths.append("Strong item synergies")
        elif analysis_data["synergy_score"] < 0.5:
            weaknesses.append("Poor item synergies")

        # Check meta compliance
        if analysis_data["meta_compliance"] > 0.6:
            strengths.append("Meta-optimized build")
        elif analysis_data["meta_compliance"] < 0.3:
            weaknesses.append("Non-meta build")

        # Check damage output
        if analysis_data["damage_analysis"]["dps"] > 800:
            strengths.append("High damage output")
        elif analysis_data["damage_analysis"]["dps"] < 400 and role in ["Mid", "Carry", "Jungle"]:
            weaknesses.append("Low damage for role")

        # Check survivability
        if analysis_data["damage_analysis"]["effective_health"] > 8000:
            strengths.append("High survivability")
        elif analysis_data["damage_analysis"]["effective_health"] < 4000 and role in [
            "Solo",
            "Support",
        ]:
            weaknesses.append("Insufficient survivability")

        # Check cost efficiency
        if total_cost <= 12000:
            strengths.append("Cost-efficient build")
        elif total_cost > 18000:
            weaknesses.append("Expensive build")

        # Power spikes
        power_spikes = []
        for item in items:
            if item.get("cost", 0) > 2500:
                power_spikes.append(f"{item['name']} (Major)")
            elif item.get("cost", 0) > 1800:
                power_spikes.append(f"{item['name']} (Minor)")

        # Generate better recommendation
        recommendation = self._generate_build_recommendation(
            analysis_data["synergy_score"],
            analysis_data["meta_compliance"],
            analysis_data["damage_analysis"],
            strengths,
            weaknesses,
        )

        return ProfessionalAnalysis(
            damage_potential=damage_potential,
            survivability=survivability,
            utility_score=utility_score,
            meta_rating=analysis_data["meta_compliance"],
            total_cost=total_cost,
            strengths=strengths or ["Balanced approach"],
            weaknesses=weaknesses or ["Minor optimization opportunities"],
            synergy_score=analysis_data["synergy_score"],
            meta_compliance=analysis_data["meta_compliance"],
            damage_simulation=analysis_data["damage_analysis"],
            power_spikes=power_spikes,
            recommendation=recommendation,
        )

    def _generate_build_recommendation(
        self,
        synergy: float,
        meta_compliance: float,
        damage: Dict[str, float],
        strengths: List[str],
        weaknesses: List[str],
    ) -> str:
        """Generate intelligent build recommendation."""
        if synergy > 0.8 and meta_compliance > 0.8 and damage["dps"] > 1000:
            return "🔥 ELITE BUILD - Professional meta with perfect synergy and high damage!"
        elif synergy > 0.7 and len(strengths) > len(weaknesses):
            return "💪 STRONG BUILD - Excellent item synergies and good composition!"
        elif meta_compliance > 0.7:
            return "📊 META BUILD - Follows professional strategies effectively!"
        elif damage["dps"] > 1000:
            return "⚔️ HIGH DAMAGE - Massive damage potential with this build!"
        elif len(strengths) > len(weaknesses):
            return "✅ SOLID BUILD - Good overall composition with minor improvements possible!"
        else:
            return "🔧 NEEDS IMPROVEMENT - Consider better item synergies and role optimization!"

    def _optimize_build_order(self, items: List[Dict[str, Any]], god_name: str) -> List[str]:
        """Optimize item build order for power progression."""
        # Sort by cost and power efficiency
        ordered_items = sorted(
            items, key=lambda x: (x.get("cost", 0), -self._calculate_item_efficiency(x))
        )
        return [item["name"] for item in ordered_items]

    def _calculate_item_efficiency(self, item: Dict[str, Any]) -> float:
        """Calculate item stat efficiency per gold."""
        stats = item.get("stats", {})
        total_stats = sum(v for v in stats.values() if isinstance(v, (int, float)))
        cost = item.get("cost", 1)
        return total_stats / cost if cost > 0 else 0

    def _generate_alternatives(
        self, alternative_items: List[Tuple[Dict[str, Any], float]]
    ) -> Dict[str, List[str]]:
        """Generate alternative item suggestions."""
        if not alternative_items:
            return {}

        alternatives: Dict[str, List[str]] = {}
        for item, score in alternative_items[:6]:
            category = item.get("category", "Other")
            if category not in alternatives:
                alternatives[category] = []
            alternatives[category].append(item["name"])

        return alternatives

    def _analyze_counters(
        self, items: List[Dict[str, Any]], enemy_comp: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Analyze what this build counters and what counters it."""
        counters: Dict[str, List[str]] = {"strong_against": [], "weak_against": [], "counter_items_needed": []}

        # Simple counter analysis
        has_anti_heal = any(
            "divine" in item.get("name", "").lower() or "pestilence" in item.get("name", "").lower()
            for item in items
        )
        has_physical_defense = any(
            item.get("stats", {}).get("physical_protection", 0) > 50 for item in items
        )
        has_magical_defense = any(
            item.get("stats", {}).get("magical_protection", 0) > 50 for item in items
        )

        if has_anti_heal:
            counters["strong_against"].append("Healing compositions")
        if has_physical_defense:
            counters["strong_against"].append("Physical damage dealers")
        if has_magical_defense:
            counters["strong_against"].append("Magical damage dealers")

        # Suggest needed counters
        if enemy_comp:
            if any("heal" in god.lower() for god in enemy_comp) and not has_anti_heal:
                counters["counter_items_needed"].append("Anti-heal items")

        return counters

    def _select_diverse_items(
        self, items: List[Tuple[Dict[str, Any], float]], count: int
    ) -> List[Dict[str, Any]]:
        """Select diverse items using intelligent selection from top-scored items."""
        if not items:
            return []

        # Take top 20 items for variety (increased from 15)
        top_items = items[: min(20, len(items))]

        selected_items: List[Dict[str, Any]] = []
        used_categories = set()

        # First pass: select core items for the role
        role_core_items = self._get_role_core_items(top_items)
        for item in role_core_items:
            if len(selected_items) >= count:
                break
            selected_items.append(item)
            used_categories.add(item.get("category", "Other"))

        # Second pass: select one item from each remaining category from top items
        for item, score in top_items:
            if len(selected_items) >= count:
                break
            category = item.get("category", "Other")
            if category not in used_categories and item not in selected_items:
                selected_items.append(item)
                used_categories.add(category)

        # Third pass: fill remaining slots with best remaining items
        remaining_slots = count - len(selected_items)
        if remaining_slots > 0:
            available_items = [item for item, score in top_items if item not in selected_items]
            selected_items.extend(available_items[:remaining_slots])

        return selected_items

    def _get_role_core_items(
        self, top_items: List[Tuple[Dict[str, Any], float]]
    ) -> List[Dict[str, Any]]:
        """Get core items that should be included for the role."""
        core_items = []

        # Get the role from the first item's context (we'll need to pass role to this method)
        # For now, we'll select based on item categories and scores

        # Always include at least one high-scoring item from each major category
        categories_found = set()
        for item, score in top_items:
            category = item.get("category", "Other")
            if category not in categories_found and score > 2.0:  # High score threshold
                core_items.append(item)
                categories_found.add(category)
                if len(core_items) >= 3:  # Limit core items
                    break

        return core_items


# Keep the original class name for compatibility
class WorkingBuildOptimizer(ProfessionalBuildOptimizer):
    """Alias for compatibility."""

    pass
