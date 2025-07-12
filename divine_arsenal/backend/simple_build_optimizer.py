#!/usr/bin/env python3
"""Simple Build Optimizer for Divine Arsenal."""

from typing import Any, Dict, List, Optional, Union

# Import both database types
from database import Database


class SimpleBuildOptimizer:
    """Simplified build optimizer that works with both Database and PostgreSQL adapter."""

    def __init__(self, db: Union[Database, Any]):
        """Initialize with database (supports both legacy Database and PostgreSQL adapter)."""
        self.db = db
        # Check if this is the PostgreSQL adapter (has app attribute)
        self.is_postgres_adapter = hasattr(db, 'app')

    def get_optimal_build(
        self, god_name: str, role: str, enemy_comp: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get an optimal build for a god and role."""
        try:
            # Get god info using appropriate method
            if self.is_postgres_adapter:
                god = self.db.get_god(god_name)
            else:
                god = self.db.get_god(god_name)
            
            if not god:
                return {"error": f"God '{god_name}' not found"}

            # Get role-based item recommendations
            build_items = self._get_role_items(role)

            # Adjust for enemy composition if provided
            if enemy_comp:
                build_items = self._adjust_for_enemies(build_items, enemy_comp)

            # Calculate build stats
            total_cost = sum(item.get("cost", 0) for item in build_items)

            return {
                "god": god_name,
                "role": role,
                "items": [item["name"] for item in build_items],
                "total_cost": total_cost,
                "build_analysis": self._analyze_build(build_items, role),
                "recommendations": self._get_build_tips(role, enemy_comp),
            }

        except Exception as e:
            return {"error": f"Build optimization failed: {e}"}

    def _get_role_items(self, role: str) -> List[Dict[str, Any]]:
        """Get recommended items for a role."""
        # Get all items using appropriate method
        if self.is_postgres_adapter:
            all_items = self.db.get_all_items()
        else:
            all_items = self.db.get_all_items()

        # Role-based item selection logic (using Smite 2 positional roles)
        role_keywords = {
            "Solo": [
                "warrior",
                "breastplate",
                "gladiator",
                "protection",
                "health",
                "guardian",
                "stone",
            ],
            "Support": [
                "guardian",
                "thebes",
                "sovereignty",
                "amulet",
                "protection",
                "stone",
                "spirit",
            ],
            "Mid": ["book", "rod", "staff", "magical", "power", "obsidian", "soul"],
            "Carry": ["bow", "devourer", "executioner", "deathbringer", "physical", "qin", "rage"],
            "Jungle": [
                "dagger",
                "jotunn",
                "heartseeker",
                "bloodforge",
                "physical",
                "bumba",
                "hydra",
            ],
            # Fallback for class-based roles if any exist
            "Warrior": ["warrior", "breastplate", "gladiator", "protection", "health"],
            "Guardian": ["guardian", "thebes", "sovereignty", "amulet", "protection"],
            "Mage": ["book", "rod", "staff", "magical", "power"],
            "Hunter": ["bow", "devourer", "executioner", "deathbringer", "physical"],
            "Assassin": ["dagger", "jotunn", "heartseeker", "bloodforge", "physical"],
        }

        keywords = role_keywords.get(role, [])
        recommended_items = []

        # Find items that match role keywords
        for item in all_items:
            item_name_lower = item["name"].lower()
            if any(keyword in item_name_lower for keyword in keywords):
                recommended_items.append(item)

        # Sort by cost and return top 6 items
        recommended_items.sort(key=lambda x: x.get("cost", 0))
        return recommended_items[:6]

    def _adjust_for_enemies(
        self, build_items: List[Dict[str, Any]], enemy_comp: List[str]
    ) -> List[Dict[str, Any]]:
        """Adjust build based on enemy composition."""
        # Get all items using appropriate method
        if self.is_postgres_adapter:
            all_items = self.db.get_all_items()
        else:
            all_items = self.db.get_all_items()

        # Analyze enemy threats
        physical_threats = 0
        magical_threats = 0

        for enemy in enemy_comp:
            # Get enemy god using appropriate method
            if self.is_postgres_adapter:
                enemy_god = self.db.get_god(enemy)
            else:
                enemy_god = self.db.get_god(enemy)
            
            if enemy_god:
                if enemy_god.get("damage_type") == "Physical":
                    physical_threats += 1
                else:
                    magical_threats += 1

        # Add counter items if needed
        counter_items = []

        if physical_threats > magical_threats:
            # Look for physical protection items
            for item in all_items:
                if (
                    "protection" in item["name"].lower()
                    and "physical" in item.get("description", "").lower()
                ):
                    counter_items.append(item)
        elif magical_threats > physical_threats:
            # Look for magical protection items
            for item in all_items:
                if (
                    "protection" in item["name"].lower()
                    and "magical" in item.get("description", "").lower()
                ):
                    counter_items.append(item)

        # Replace one offensive item with a counter item if available
        if counter_items and len(build_items) > 0:
            build_items[-1] = counter_items[0]

        return build_items

    def _analyze_build(self, build_items: List[Dict[str, Any]], role: str) -> Dict[str, Any]:
        """Analyze the build and provide insights."""
        total_cost = sum(item.get("cost", 0) for item in build_items)

        # Basic analysis
        analysis = {
            "total_cost": total_cost,
            "item_count": len(build_items),
            "cost_efficiency": "Good" if total_cost < 12000 else "Expensive",
            "role_fit": "Excellent",  # Simplified for now
            "power_spike": "Mid Game" if total_cost < 10000 else "Late Game",
        }

        return analysis

    def _get_build_tips(self, role: str, enemy_comp: Optional[List[str]] = None) -> List[str]:
        """Get build tips and recommendations."""
        tips = []

        # Role-specific tips (Smite 2 positional roles)
        role_tips = {
            "Solo": [
                "Focus on early game presence with defensive items",
                "Build hybrid damage and protection for team fights",
                "Consider cooldown reduction for ability spam",
            ],
            "Support": [
                "Prioritize team utility and protection items",
                "Build aura items to help your team",
                "Focus on initiation and peel potential",
            ],
            "Mid": [
                "Rush power items for burst damage",
                "Consider penetration against tanky enemies",
                "Build some survivability for late game",
            ],
            "Carry": [
                "Start with lifesteal for sustain",
                "Build attack speed and critical chance",
                "Consider penetration for late game",
            ],
            "Jungle": [
                "Focus on early game power spikes",
                "Build penetration and power",
                "Consider some survivability items",
            ],
            # Fallback for class-based roles
            "Warrior": [
                "Focus on early game presence with defensive items",
                "Build hybrid damage and protection for team fights",
                "Consider cooldown reduction for ability spam",
            ],
            "Guardian": [
                "Prioritize team utility and protection items",
                "Build aura items to help your team",
                "Focus on initiation and peel potential",
            ],
            "Mage": [
                "Rush power items for burst damage",
                "Consider penetration against tanky enemies",
                "Build some survivability for late game",
            ],
            "Hunter": [
                "Start with lifesteal for sustain",
                "Build attack speed and critical chance",
                "Consider penetration for late game",
            ],
            "Assassin": [
                "Focus on early game power spikes",
                "Build penetration and power",
                "Consider some survivability items",
            ],
        }

        tips.extend(role_tips.get(role, ["Build items appropriate for your god and role"]))

        # Enemy-specific tips
        if enemy_comp:
            tips.append(f"Consider counter-building against {', '.join(enemy_comp)}")

        return tips

    def get_god_builds(self, god_name: str) -> Dict[str, Any]:
        """Get popular builds for a god."""
        try:
            # Get god info using appropriate method
            if self.is_postgres_adapter:
                god = self.db.get_god(god_name)
            else:
                god = self.db.get_god(god_name)
            
            if not god:
                return {"error": f"God '{god_name}' not found"}

            # Simple build recommendations based on god type
            builds = {
                "recommended": {
                    "build": ["Rod of Tahuti", "Book of Thoth", "Chronos' Pendant"],
                    "description": "Standard magical power build",
                },
                "counter": {
                    "build": ["Void Stone", "Divine Ruin", "Obsidian Shard"],
                    "description": "Penetration and counter-healing build",
                },
            }

            return {"god": god_name, "builds": builds}

        except Exception as e:
            return {"error": f"Failed to get builds for {god_name}: {e}"}
