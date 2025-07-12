"""Item data access layer for Divine Arsenal build optimizer."""

from typing import Any, Dict, List, Optional

from divine_arsenal.backend.database import Database
from divine_arsenal.backend.item import Item


class ItemData:
    """Manages item data for the build optimizer."""

    def __init__(self, db: Database):
        self.db = db
        self._items_cache: Optional[List[Item]] = None

    def get_all_items(self) -> List[Item]:
        """Get all items from the database."""
        if self._items_cache is None:
            raw_items = self.db.get_all_items()
            self._items_cache = [Item.from_db_row(item) for item in raw_items] if raw_items else []
        return self._items_cache or []

    def get_item(self, name: str) -> Optional[Item]:
        """Get a specific item by name."""
        items = self.get_all_items()
        for item in items:
            if item.name.lower() == name.lower():
                return item
        return None

    def get_items_by_category(self, category: str) -> List[Item]:
        """Get all items of a specific category."""
        items = self.get_all_items()
        return [item for item in items if item.category.lower() == category.lower()]

    def get_items_by_tier(self, tier: int) -> List[Item]:
        """Get all items of a specific tier."""
        items = self.get_all_items()
        return [item for item in items if item.tier == tier]

    def get_items_by_tag(self, tag: str) -> List[Item]:
        """Get all items with a specific tag."""
        items = self.get_all_items()
        return [
            item for item in items if item.tags and tag.lower() in [t.lower() for t in item.tags]
        ]

    def get_items_by_cost_range(self, min_cost: int, max_cost: int) -> List[Item]:
        """Get all items within a cost range."""
        items = self.get_all_items()
        return [item for item in items if min_cost <= item.cost <= max_cost]

    def get_starter_items(self) -> List[Item]:
        """Get all starter items (tier 0)."""
        return self.get_items_by_tier(0)

    def get_offensive_items(self) -> List[Item]:
        """Get all offensive items."""
        return [
            item
            for item in self.get_all_items()
            if item.physical_power > 0
            or item.magical_power > 0
            or item.attack_speed > 0
            or item.penetration > 0
            or item.crit_chance > 0
        ]

    def get_defensive_items(self) -> List[Item]:
        """Get all defensive items."""
        return [
            item
            for item in self.get_all_items()
            if item.physical_protection > 0 or item.magical_protection > 0 or item.health > 0
        ]

    def get_items_with_stat(self, stat_name: str, min_value: float = 0.1) -> List[Item]:
        """Get all items that provide a specific stat above minimum value."""
        result = []
        for item in self.get_all_items():
            stat_value = getattr(item, stat_name, 0.0)
            if stat_value >= min_value:
                result.append(item)
        return result

    def get_items_by_tags(self, tags: List[str]) -> List[Item]:
        """Get all items that have any of the specified tags."""
        items = self.get_all_items()
        return [
            item
            for item in items
            if item.tags and any(tag.lower() in [t.lower() for t in item.tags] for tag in tags)
        ]

    def get_physical_items(self) -> List[Item]:
        """Get all physical items."""
        return self.get_items_by_tag("Physical")

    def get_magical_items(self) -> List[Item]:
        """Get all magical items."""
        return self.get_items_by_tag("Magical")

    def get_relic_items(self) -> List[Item]:
        """Get all relic items."""
        return self.get_items_by_category("Relic")

    def get_consumable_items(self) -> List[Item]:
        """Get all consumable items."""
        return self.get_items_by_category("Consumable")

    def refresh_cache(self) -> None:
        """Refresh the items cache."""
        self._items_cache = None
