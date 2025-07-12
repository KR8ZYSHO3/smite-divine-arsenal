"""Build class for Divine Arsenal build optimizer."""

from dataclasses import dataclass, field
from typing import Dict, List

from divine_arsenal.backend.item import Item, ItemStats


@dataclass
class Build:
    """Represents a Smite build with items and calculated stats."""

    items: List[Item] = field(default_factory=list)
    total_cost: int = 0
    win_rate: float = 0.0
    popularity: float = 0.0

    def __post_init__(self):
        """Calculate total cost if not provided."""
        if self.total_cost == 0 and self.items:
            self.total_cost = sum(item.cost for item in self.items)

    @property
    def stats_summary(self) -> ItemStats:
        """Calculate the combined stats of all items in the build."""
        combined_stats: ItemStats = {
            "physical_power": 0.0,
            "magical_power": 0.0,
            "physical_prot": 0.0,
            "magical_prot": 0.0,
            "health": 0.0,
            "mana": 0.0,
            "movement_speed": 0.0,
            "attack_speed": 0.0,
            "cooldown": 0.0,
            "physical_pen": 0.0,
            "magical_pen": 0.0,
            "physical_lifesteal": 0.0,
            "magical_lifesteal": 0.0,
            "crit_chance": 0.0,
            "crit_damage": 0.0,
        }

        for item in self.items:
            item_stats = item.stats
            for stat, value in item_stats.items():
                combined_stats[stat] += value

        return combined_stats

    @property
    def item_names(self) -> List[str]:
        """Get list of item names in the build."""
        return [item.name for item in self.items]

    def add_item(self, item: Item) -> None:
        """Add an item to the build."""
        self.items.append(item)
        self.total_cost += item.cost

    def remove_item(self, item: Item) -> bool:
        """Remove an item from the build. Returns True if item was found and removed."""
        if item in self.items:
            self.items.remove(item)
            self.total_cost -= item.cost
            return True
        return False

    def replace_item(self, old_item: Item, new_item: Item) -> bool:
        """Replace an item in the build. Returns True if replacement was successful."""
        for i, item in enumerate(self.items):
            if item == old_item:
                self.items[i] = new_item
                self.total_cost = self.total_cost - old_item.cost + new_item.cost
                return True
        return False

    def clear(self) -> None:
        """Clear all items from the build."""
        self.items.clear()
        self.total_cost = 0

    def is_full(self, max_items: int = 6) -> bool:
        """Check if the build has the maximum number of items."""
        return len(self.items) >= max_items

    def can_afford(self, item: Item, max_gold: int = 15000) -> bool:
        """Check if the build can afford an additional item."""
        return self.total_cost + item.cost <= max_gold

    def to_dict(self) -> Dict:
        """Convert build to dictionary for serialization."""
        return {
            "items": [item.name for item in self.items],
            "total_cost": self.total_cost,
            "stats_summary": self.stats_summary,
            "win_rate": self.win_rate,
            "popularity": self.popularity,
        }
