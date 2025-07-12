"""Item classes for Divine Arsenal build optimizer."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Type alias for item stats
ItemStats = Dict[str, float]


@dataclass
class Item:
    """Represents a Smite 2 item with all its properties."""

    name: str
    cost: int
    tier: int  # Changed from str to int to match Smite 2
    category: str
    passive: str = ""

    # Stats - now from nested stats object
    stats: Optional[Dict[str, float]] = None

    # Tags from Smite 2 data
    tags: Optional[List[str]] = None

    def __post_init__(self):
        """Initialize stats and tags if not provided."""
        if self.stats is None:
            self.stats = {}
        if self.tags is None:
            self.tags = []

    @property
    def physical_power(self) -> float:
        """Get physical power from stats."""
        return (self.stats or {}).get("physical_power", 0.0)

    @property
    def magical_power(self) -> float:
        """Get magical power from stats."""
        return (self.stats or {}).get("magical_power", 0.0)

    @property
    def physical_protection(self) -> float:
        """Get physical protection from stats."""
        return (self.stats or {}).get("physical_protection", 0.0)

    @property
    def magical_protection(self) -> float:
        """Get magical protection from stats."""
        return (self.stats or {}).get("magical_protection", 0.0)

    @property
    def health(self) -> float:
        """Get health from stats."""
        return (self.stats or {}).get("health", 0.0)

    @property
    def mana(self) -> float:
        """Get mana from stats."""
        return (self.stats or {}).get("mana", 0.0)

    @property
    def movement_speed(self) -> float:
        """Get movement speed from stats."""
        return (self.stats or {}).get("movement_speed", 0.0)

    @property
    def attack_speed(self) -> float:
        """Get attack speed from stats."""
        return (self.stats or {}).get("attack_speed", 0.0)

    @property
    def cooldown_reduction(self) -> float:
        """Get cooldown reduction from stats."""
        return (self.stats or {}).get("cooldown_reduction", 0.0)

    @property
    def penetration(self) -> float:
        """Get penetration from stats."""
        return (self.stats or {}).get("penetration", 0.0)

    @property
    def lifesteal(self) -> float:
        """Get lifesteal from stats."""
        return (self.stats or {}).get("lifesteal", 0.0)

    @property
    def crit_chance(self) -> float:
        """Get critical chance from stats."""
        return (self.stats or {}).get("critical_chance", 0.0)

    @property
    def crit_damage(self) -> float:
        """Get critical damage from stats."""
        return (self.stats or {}).get("critical_damage", 0.0)

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "Item":
        """Create an Item from a database row."""
        # Extract stats from nested dict if present, otherwise from individual fields
        stats = row.get("stats", {})
        if not stats:
            # Fallback to individual stat fields for backward compatibility
            stats = {
                "physical_power": row.get("physical_power", 0.0),
                "magical_power": row.get("magical_power", 0.0),
                "physical_protection": row.get("physical_protection", 0.0),
                "magical_protection": row.get("magical_protection", 0.0),
                "health": row.get("health", 0.0),
                "mana": row.get("mana", 0.0),
                "movement_speed": row.get("movement_speed", 0.0),
                "attack_speed": row.get("attack_speed", 0.0),
                "cooldown_reduction": row.get("cooldown_reduction", 0.0),
                "penetration": row.get("penetration", 0.0),
                "lifesteal": row.get("lifesteal", 0.0),
                "critical_chance": row.get("crit_chance", 0.0),
                "critical_damage": row.get("crit_damage", 0.0),
            }

        return cls(
            name=row.get("name", ""),
            cost=row.get("cost", 0),
            tier=row.get("tier", 0),  # Default to 0 for tier
            category=row.get("category", ""),
            passive=row.get("passive", ""),
            stats=stats,
            tags=row.get("tags", []),
        )

    @classmethod
    def from_smite2_data(cls, data: Dict[str, Any]) -> "Item":
        """Create an Item from Smite 2 JSON data."""
        return cls(
            name=data.get("name", ""),
            cost=data.get("cost", 0),
            tier=data.get("tier", 0),
            category=data.get("category", ""),
            passive=data.get("passive", ""),
            stats=data.get("stats", {}),
            tags=data.get("tags", []),
        )
