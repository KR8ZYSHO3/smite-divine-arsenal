#!/usr/bin/env python3
"""
Multi-Mode Optimizer for SMITE 2 Build Optimizer
"""

from enum import Enum
from typing import Any, Dict, List


class GameMode(Enum):
    CONQUEST = "conquest"
    ARENA = "arena"
    JOUST = "joust"
    ASSAULT = "assault"


class MultiModeOptimizer:
    """Optimizes builds for different game modes."""

    def __init__(self):
        self.mode_weights = {
            GameMode.CONQUEST: {
                "sustain": 1.0,
                "burst": 1.0,
                "team_fight": 1.0,
                "cost_efficiency": 1.0,
            },
            GameMode.ARENA: {
                "sustain": 1.4,  # Higher sustain for constant fighting
                "burst": 1.2,
                "team_fight": 1.5,  # Critical for Arena
                "cost_efficiency": 0.9,
            },
            GameMode.JOUST: {
                "sustain": 1.2,
                "burst": 1.3,  # Higher burst for 3v3
                "team_fight": 1.1,
                "cost_efficiency": 1.0,
            },
            GameMode.ASSAULT: {
                "sustain": 2.0,  # Critical - no backing
                "burst": 0.9,
                "team_fight": 1.4,
                "cost_efficiency": 1.3,
            },
        }

        self.sustain_items = ["Bloodforge", "Soul Eater", "Bancroft's Talon"]
        self.burst_items = ["Rod of Tahuti", "Soul Reaver", "Heartseeker", "Deathbringer"]
        self.team_fight_items = ["Lotus Crown", "Sovereignty", "Gauntlet of Thebes"]

    def optimize_for_mode(self, base_build: Dict[str, Any], mode: GameMode) -> Dict[str, Any]:
        """Optimize build for specific game mode."""

        optimized_build = base_build.copy()
        mode_weights = self.mode_weights[mode]

        # Adjust items based on mode
        items = optimized_build.get("items", [])
        adjusted_items = self._adjust_items_for_mode(items, mode)

        optimized_build["items"] = adjusted_items
        optimized_build["mode"] = mode.value
        optimized_build["mode_adjustments"] = []

        # Calculate mode-adjusted score
        original_score = base_build.get("meta_score", 50)
        mode_bonus = self._calculate_mode_bonus(adjusted_items, mode_weights)
        optimized_build["meta_score"] = min(100, original_score + mode_bonus)

        return optimized_build

    def _adjust_items_for_mode(self, items: List[str], mode: GameMode) -> List[str]:
        """Adjust items based on mode requirements."""

        adjusted_items = items.copy()

        if mode == GameMode.ARENA:
            # Add sustain for constant fighting
            if not any(item in self.sustain_items for item in adjusted_items):
                adjusted_items[0] = "Bloodforge"

        elif mode == GameMode.JOUST:
            # Prioritize burst for 3v3
            burst_count = sum(1 for item in adjusted_items if item in self.burst_items)
            if burst_count < 2:
                adjusted_items.append("Heartseeker")

        elif mode == GameMode.ASSAULT:
            # Force sustain items
            if not any(item in self.sustain_items for item in adjusted_items):
                adjusted_items.insert(0, "Soul Eater")

        return adjusted_items

    def _calculate_mode_bonus(self, items: List[str], weights: Dict[str, float]) -> float:
        """Calculate bonus score based on mode compatibility."""

        bonus = 0.0

        # Sustain bonus
        sustain_items = [item for item in items if item in self.sustain_items]
        bonus += len(sustain_items) * weights["sustain"] * 3

        # Burst bonus
        burst_items = [item for item in items if item in self.burst_items]
        bonus += len(burst_items) * weights["burst"] * 2

        # Team fight bonus
        team_fight_items = [item for item in items if item in self.team_fight_items]
        bonus += len(team_fight_items) * weights["team_fight"] * 2

        return bonus


def test_multi_mode():
    """Test multi-mode optimization."""

    optimizer = MultiModeOptimizer()

    # Sample Hecate build
    base_build = {
        "god": "Hecate",
        "role": "Mid",
        "items": ["Book of Thoth", "Spear of Desolation", "Divine Ruin", "Rod of Tahuti"],
        "meta_score": 75,
    }

    print("🎮 MULTI-MODE OPTIMIZATION TEST")
    print("=" * 50)
    print(f"Base Build: {base_build['god']} {base_build['role']}")
    print(f"Original Score: {base_build['meta_score']}")

    for mode in GameMode:
        optimized = optimizer.optimize_for_mode(base_build, mode)
        print(f"\n{mode.value.upper()}:")
        print(f"  Score: {optimized['meta_score']}")
        print(f"  Items: {optimized['items'][:3]}")


if __name__ == "__main__":
    test_multi_mode()
