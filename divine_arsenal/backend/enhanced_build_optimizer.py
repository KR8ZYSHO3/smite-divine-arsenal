#!/usr/bin/env python3
"""
Enhanced Build Optimizer for SMITE 2 Divine Arsenal
Implements Grok's recommendations for statistical modeling with real-time analysis
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from working_build_optimizer import WorkingBuildOptimizer
from database import Database

logger = logging.getLogger(__name__)


@dataclass
class EnemyComposition:
    """Real-time enemy composition analysis."""
    gods: List[str]
    roles: Dict[str, str]
    detected_items: Dict[str, List[str]]
    composition_type: str  # e.g., "heavy_physical", "healing_comp", "burst_comp"
    threat_level: float  # 0.0 to 1.0
    last_updated: datetime


@dataclass
class RealTimeBuildRecommendation:
    """Real-time build recommendation with enemy analysis."""
    core_build: List[str]
    situational_items: List[str]
    counter_items: List[str]
    enemy_analysis: EnemyComposition
    confidence_score: float
    reasoning: List[str]
    meta_compliance: float
    last_updated: datetime


class EnhancedBuildOptimizer(WorkingBuildOptimizer):
    """
    Enhanced Build Optimizer with Real-Time Analysis
    
    Implements Grok's recommendations:
    - Statistical modeling (no neural networks)
    - Real-time enemy composition analysis
    - Tracker.gg integration for live data
    - Counter-building intelligence
    - Meta compliance scoring
    """
    
    def __init__(self, db: Database):
        super().__init__(db)
        self.enemy_cache = {}  # Cache enemy compositions
        self.cache_duration = 300  # 5 minutes
        self._init_enhanced_counter_rules()
        self._init_meta_analysis_rules()
        
    def _init_enhanced_counter_rules(self):
        """Enhanced counter-building rules based on Grok's analysis."""
        self.enhanced_counters = {
            # Anti-Healing (80% reduction meta)
            "healing_comp": {
                "items": ["Divine Ruin", "Brawler's Beat Stick", "Contagion"],
                "priority": 0.9,
                "reasoning": "80% anti-heal reduction is meta-dominant"
            },
            # Anti-Physical Damage
            "heavy_physical": {
                "items": ["Sovereignty", "Midgardian Mail", "Witchblade"],
                "priority": 0.8,
                "reasoning": "Physical damage heavy composition detected"
            },
            # Anti-Magical Damage
            "heavy_magical": {
                "items": ["Heartward Amulet", "Pestilence", "Runic Shield"],
                "priority": 0.8,
                "reasoning": "Magical damage heavy composition detected"
            },
            # Anti-Critical Strike
            "crit_heavy": {
                "items": ["Spectral Armor", "Midgardian Mail"],
                "priority": 0.7,
                "reasoning": "Critical strike based carry detected"
            },
            # Anti-Mobility
            "high_mobility": {
                "items": ["Frostbound Hammer", "Gem of Isolation"],
                "priority": 0.6,
                "reasoning": "High mobility enemy composition"
            },
            # Anti-Burst
            "burst_comp": {
                "items": ["Mantle of Discord", "Spirit Robe", "Hide of the Nemean Lion"],
                "priority": 0.7,
                "reasoning": "Burst damage composition detected"
            }
        }
    
    def _init_meta_analysis_rules(self):
        """Meta analysis rules for current SMITE 2 meta."""
        self.meta_rules = {
            "current_patch": "OB9",
            "meta_focus": {
                "early_game": ["Hunter's Cowl", "Vampiric Shroud", "Warrior's Axe"],
                "mid_game": ["Penetration items", "Cooldown Reduction"],
                "late_game": ["Titan's Bane", "Obsidian Shard", "Rod of Tahuti"]
            },
            "role_priorities": {
                "Jungle": "Early pressure and ganking",
                "Mid": "Wave clear and roaming",
                "Carry": "Safe farming and scaling",
                "Support": "Team utility and protection",
                "Solo": "Sustain and frontline presence"
            }
        }
    
    def analyze_enemy_composition_real_time(
        self, 
        enemy_gods: List[str], 
        detected_items: Optional[Dict[str, List[str]]] = None
    ) -> EnemyComposition:
        """
        Real-time enemy composition analysis.
        
        Args:
            enemy_gods: List of enemy god names
            detected_items: Dict of god_name -> list of detected items
            
        Returns:
            EnemyComposition with analysis
        """
        try:
            # Defensive: ensure enemy_gods is a list of strings
            if not enemy_gods:
                enemy_gods = []
            
            # Convert any non-string items to strings (handles dict objects)
            clean_enemy_gods = []
            for god in enemy_gods:
                if isinstance(god, dict):
                    # If it's a dict, try to get the name
                    god_name = god.get("name") or god.get("god_name") or str(god)
                    clean_enemy_gods.append(str(god_name))
                else:
                    clean_enemy_gods.append(str(god))
            
            # Check cache first - ensure all items are strings for hashable key
            cache_key = tuple(sorted(clean_enemy_gods))
            if cache_key in self.enemy_cache:
                cached = self.enemy_cache[cache_key]
                if datetime.now() - cached.last_updated < timedelta(seconds=self.cache_duration):
                    return cached
            
            # Analyze enemy gods
            roles = {}
            damage_types = {"physical": 0, "magical": 0}
            healing_gods = 0
            mobility_gods = 0
            burst_gods = 0
            
            for god_name in clean_enemy_gods:
                god = self.db.get_god(god_name)
                if god:
                    role = god.get("role", "Unknown")
                    damage_type = god.get("damage_type", "Physical")
                    roles[god_name] = role
                    
                    if damage_type == "Physical":
                        damage_types["physical"] += 1
                    else:
                        damage_types["magical"] += 1
                    
                    # Check for healing gods
                    if any(healer in god_name.lower() for healer in ["aphrodite", "hel", "ra", "chang'e"]):
                        healing_gods += 1
                    
                    # Check for high mobility gods
                    if any(mobile in god_name.lower() for mobile in ["mercury", "serqet", "awilix", "ratatoskr"]):
                        mobility_gods += 1
                    
                    # Check for burst gods
                    if any(burst in god_name.lower() for burst in ["scylla", "he bo", "anubis", "zeus"]):
                        burst_gods += 1
            
            # Determine composition type
            composition_type = "balanced"
            threat_level = 0.5
            
            if healing_gods >= 2:
                composition_type = "healing_comp"
                threat_level = 0.9
            elif damage_types["physical"] >= 3:
                composition_type = "heavy_physical"
                threat_level = 0.8
            elif damage_types["magical"] >= 3:
                composition_type = "heavy_magical"
                threat_level = 0.8
            elif mobility_gods >= 2:
                composition_type = "high_mobility"
                threat_level = 0.7
            elif burst_gods >= 2:
                composition_type = "burst_comp"
                threat_level = 0.8
            
            # Create composition object
            composition = EnemyComposition(
                gods=clean_enemy_gods,
                roles=roles,
                detected_items=detected_items or {},
                composition_type=composition_type,
                threat_level=threat_level,
                last_updated=datetime.now()
            )
            
            # Cache the result
            self.enemy_cache[cache_key] = composition
            
            logger.info(f"Enemy composition analyzed: {composition_type} (threat: {threat_level})")
            return composition
            
        except Exception as e:
            logger.error(f"Error analyzing enemy composition: {e}")
            return EnemyComposition(
                gods=clean_enemy_gods if 'clean_enemy_gods' in locals() else [],
                roles={},
                detected_items={},
                composition_type="unknown",
                threat_level=0.5,
                last_updated=datetime.now()
            )
    
    def optimize_build_real_time(
        self,
        god_name: str,
        role: str,
        enemy_gods: List[str],
        detected_items: Optional[Dict[str, List[str]]] = None,
        budget: int = 15000,
        playstyle: str = "meta"
    ) -> RealTimeBuildRecommendation:
        """
        Real-time build optimization with enemy composition analysis.
        
        Args:
            god_name: Name of the god
            role: Role (Mid, Solo, Support, Carry, Jungle)
            enemy_gods: List of enemy god names
            detected_items: Dict of detected enemy items
            budget: Gold budget
            playstyle: "meta", "aggressive", "defensive", "utility"
            
        Returns:
            RealTimeBuildRecommendation with optimized build
        """
        try:
            logger.info(f"Real-time build optimization for {god_name} ({role}) vs {enemy_gods}")
            
            # Analyze enemy composition
            enemy_comp = self.analyze_enemy_composition_real_time(enemy_gods, detected_items)
            
            # Get base optimization
            base_result = self.optimize_build(
                god_name=god_name,
                role=role,
                enemy_comp=enemy_gods,
                budget=budget
            )
            
            if "error" in base_result:
                return RealTimeBuildRecommendation(
                    core_build=[],
                    situational_items=[],
                    counter_items=[],
                    enemy_analysis=enemy_comp,
                    confidence_score=0.0,
                    reasoning=[f"Error: {base_result['error']}"],
                    meta_compliance=0.0,
                    last_updated=datetime.now()
                )
            
            # Extract items from base result - handle both list and dict formats
            core_build = []
            items = base_result.get("items", [])
            
            if isinstance(items, list):
                # Handle list of items (could be strings or dicts)
                for item in items:
                    if isinstance(item, dict):
                        # Item is a dict with 'item_name' or 'name' field
                        item_name = item.get("item_name") or item.get("name")
                        if item_name:
                            core_build.append(item_name)
                    elif isinstance(item, str):
                        # Item is already a string
                        core_build.append(item)
                    else:
                        # Convert to string as fallback
                        core_build.append(str(item))
            
            # Generate counter items based on enemy composition
            counter_items = self._generate_counter_items(enemy_comp, role)
            if not isinstance(counter_items, list):
                counter_items = []
            
            # Generate situational items
            situational_items = self._generate_situational_items(enemy_comp, role, playstyle)
            if not isinstance(situational_items, list):
                situational_items = []
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                enemy_comp, base_result, len(core_build)
            )
            
            # Generate reasoning
            reasoning = self._generate_real_time_reasoning(
                enemy_comp, base_result, counter_items
            )
            if not isinstance(reasoning, list):
                reasoning = [str(reasoning)]
            
            # Calculate meta compliance
            meta_compliance = self._calculate_meta_compliance(core_build, role)
            
            return RealTimeBuildRecommendation(
                core_build=core_build,
                situational_items=situational_items,
                counter_items=counter_items,
                enemy_analysis=enemy_comp,
                confidence_score=confidence_score,
                reasoning=reasoning,
                meta_compliance=meta_compliance,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error in real-time build optimization: {e}")
            return RealTimeBuildRecommendation(
                core_build=[],
                situational_items=[],
                counter_items=[],
                enemy_analysis=EnemyComposition(
                    gods=enemy_gods,
                    roles={},
                    detected_items={},
                    composition_type="error",
                    threat_level=0.0,
                    last_updated=datetime.now()
                ),
                confidence_score=0.0,
                reasoning=[f"Error: {str(e)}"],
                meta_compliance=0.0,
                last_updated=datetime.now()
            )
    
    def _generate_counter_items(self, enemy_comp: EnemyComposition, role: str) -> List[str]:
        """Generate counter items based on enemy composition."""
        counter_items = []
        
        # Get counter rules for this composition type
        counter_rule = self.enhanced_counters.get(enemy_comp.composition_type)
        if counter_rule:
            # Filter items by role appropriateness
            role_priorities = self.role_priorities.get(role, {})
            avoid_categories = role_priorities.get("avoid_categories", [])
            
            for item_name in counter_rule["items"]:
                item = self.db.get_item(item_name)
                if item:
                    category = item.get("category", "")
                    if category not in avoid_categories:
                        counter_items.append(item_name)
        
        return counter_items[:3]  # Limit to 3 counter items
    
    def _generate_situational_items(self, enemy_comp: EnemyComposition, role: str, playstyle: str) -> List[str]:
        """Generate situational items based on playstyle and enemy composition."""
        situational_items = []
        
        # Role-specific situational items
        if role == "Support":
            if enemy_comp.composition_type == "healing_comp":
                situational_items.extend(["Pestilence", "Contagion"])
            if enemy_comp.composition_type == "heavy_physical":
                situational_items.append("Sovereignty")
            if enemy_comp.composition_type == "heavy_magical":
                situational_items.append("Heartward Amulet")
        
        elif role == "Mid":
            if enemy_comp.composition_type == "healing_comp":
                situational_items.append("Divine Ruin")
            if playstyle == "aggressive":
                situational_items.extend(["Soul Reaver", "Rod of Tahuti"])
            if playstyle == "defensive":
                situational_items.extend(["Mantle of Discord", "Spirit Robe"])
        
        elif role == "Carry":
            if enemy_comp.composition_type == "healing_comp":
                situational_items.append("Brawler's Beat Stick")
            if enemy_comp.composition_type == "crit_heavy":
                situational_items.append("Spectral Armor")
        
        return situational_items[:3]  # Limit to 3 situational items
    
    def _calculate_confidence_score(
        self, 
        enemy_comp: EnemyComposition, 
        base_result: Dict[str, Any], 
        item_count: int
    ) -> float:
        """Calculate confidence score for the recommendation."""
        base_score = 0.7  # Base confidence
        
        # Adjust based on enemy composition analysis quality
        if enemy_comp.composition_type != "unknown":
            base_score += 0.1
        
        # Adjust based on threat level
        if enemy_comp.threat_level > 0.7:
            base_score += 0.1  # High threat = more confident in counters
        
        # Adjust based on item count
        if item_count >= 6:
            base_score += 0.1
        
        # Adjust based on base result quality
        if "score" in base_result:
            score = base_result["score"]
            if score > 80:
                base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _generate_real_time_reasoning(
        self, 
        enemy_comp: EnemyComposition, 
        base_result: Dict[str, Any], 
        counter_items: List[str]
    ) -> List[str]:
        """Generate reasoning for the real-time recommendation."""
        reasoning = []
        
        try:
            # Defensive: ensure counter_items is a list of strings
            if not isinstance(counter_items, list):
                counter_items = []
            
            # Convert any non-string items to strings
            clean_counter_items = []
            for item in counter_items:
                if isinstance(item, dict):
                    item_name = item.get("name") or item.get("item_name") or str(item)
                    clean_counter_items.append(str(item_name))
                else:
                    clean_counter_items.append(str(item))
            
            # Enemy composition reasoning
            if enemy_comp.composition_type and enemy_comp.composition_type != "unknown":
                reasoning.append(f"Enemy composition: {enemy_comp.composition_type} (threat level: {enemy_comp.threat_level:.1f})")
            
            # Counter item reasoning
            if clean_counter_items:
                reasoning.append(f"Recommended counters: {', '.join(clean_counter_items)}")
            
            # Base optimization reasoning
            if isinstance(base_result, dict) and "explanation" in base_result:
                explanation = base_result["explanation"]
                if isinstance(explanation, str):
                    reasoning.append(f"Base optimization: {explanation}")
                elif isinstance(explanation, (list, tuple)):
                    # Handle list/tuple explanations
                    reasoning.append(f"Base optimization: {', '.join(str(x) for x in explanation)}")
            
            # Meta compliance
            if isinstance(base_result, dict) and "meta_compliance" in base_result:
                meta_score = base_result["meta_compliance"]
                if isinstance(meta_score, (int, float)):
                    reasoning.append(f"Meta compliance: {meta_score:.1f}/1.0")
            
            # Ensure we always return a list of strings
            return [str(reason) for reason in reasoning]
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return [f"Real-time optimization completed with {len(clean_counter_items) if 'clean_counter_items' in locals() else 0} counter items"]
    
    def _calculate_meta_compliance(self, items: List[str], role: str) -> float:
        """Calculate meta compliance score for the build."""
        if not items:
            return 0.0
        
        # Get meta items for this role
        meta_items = self.meta_rules["meta_focus"].get("mid_game", [])
        
        # Count meta items in build
        meta_count = sum(1 for item in items if item in meta_items)
        
        # Calculate compliance score
        compliance = meta_count / len(items) if items else 0.0
        
        return min(compliance, 1.0)
    
    def get_recommendation_summary(self, recommendation: RealTimeBuildRecommendation) -> Dict[str, Any]:
        """Get a summary of the real-time recommendation."""
        return {
            "god": recommendation.enemy_analysis.gods[0] if recommendation.enemy_analysis.gods else "Unknown",
            "role": "Unknown",
            "core_build": recommendation.core_build,
            "situational_items": recommendation.situational_items,
            "counter_items": recommendation.counter_items,
            "enemy_composition": recommendation.enemy_analysis.composition_type,
            "threat_level": recommendation.enemy_analysis.threat_level,
            "confidence_score": recommendation.confidence_score,
            "meta_compliance": recommendation.meta_compliance,
            "reasoning": recommendation.reasoning,
            "last_updated": recommendation.last_updated.isoformat(),
            "cache_duration": self.cache_duration
        } 