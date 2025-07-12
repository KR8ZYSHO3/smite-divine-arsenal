"""Module for handling god-specific build templates and recommendations."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from divine_arsenal.backend.build import Build
from divine_arsenal.backend.item import Item
from divine_arsenal.backend.item_stats import ItemStats


@dataclass
class GodTemplate:
    """Represents a god-specific build template."""

    god_name: str
    role: str
    core_items: List[str]  # List of item names that are core to the build
    situational_items: List[str]  # List of situational items
    counter_items: Dict[str, List[str]]  # Dict of enemy role -> counter items
    power_spike_items: List[str]  # Items that provide early power spikes
    late_game_items: List[str]  # Items that are better late game


class GodTemplateManager:
    """Manages god-specific build templates and recommendations."""

    def __init__(self):
        self.templates: Dict[str, Dict[str, GodTemplate]] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default templates for common gods."""
        # Example template for Thor
        thor_template = GodTemplate(
            god_name="Thor",
            role="Assassin",
            core_items=["Jotunn's Wrath", "Hydra's Lament", "The Crusher"],
            situational_items=["Brawler's Beat Stick", "Titan's Bane", "Heartseeker"],
            counter_items={
                "Mage": ["Magi's Cloak", "Ancile"],
                "Hunter": ["Hide of the Nemean Lion", "Midgardian Mail"],
                "Assassin": ["Hide of the Nemean Lion", "Magi's Cloak"],
            },
            power_spike_items=["Jotunn's Wrath", "Hydra's Lament"],
            late_game_items=["Titan's Bane", "Heartseeker"],
        )
        self.templates.setdefault("Thor", {})["Assassin"] = thor_template

        # Add more templates as needed

    def get_template(self, god_name: str, role: str) -> Optional[GodTemplate]:
        """Get the template for a specific god and role."""
        return self.templates.get(god_name, {}).get(role)

    def get_core_items(self, god_name: str, role: str) -> List[str]:
        """Get core items for a specific god and role."""
        template = self.get_template(god_name, role)
        return template.core_items if template else []

    def get_situational_items(self, god_name: str, role: str) -> List[str]:
        """Get situational items for a specific god and role."""
        template = self.get_template(god_name, role)
        return template.situational_items if template else []

    def get_counter_items(self, god_name: str, role: str, enemy_role: str) -> List[str]:
        """Get counter items for a specific god against an enemy role."""
        template = self.get_template(god_name, role)
        return template.counter_items.get(enemy_role, []) if template else []

    def get_power_spike_items(self, god_name: str, role: str) -> List[str]:
        """Get items that provide early power spikes for a specific god and role."""
        template = self.get_template(god_name, role)
        return template.power_spike_items if template else []

    def get_late_game_items(self, god_name: str, role: str) -> List[str]:
        """Get items that are better late game for a specific god and role."""
        template = self.get_template(god_name, role)
        return template.late_game_items if template else []

    def create_build_from_template(
        self, god_name: str, role: str, enemy_comp: List[str], available_items: List[Item]
    ) -> Optional[Build]:
        """Create a build based on the god's template and enemy composition."""
        template = self.get_template(god_name, role)
        if not template:
            return None

        # Create a list to store selected items
        selected_items: List[Item] = []

        # Add core items
        for item_name in template.core_items:
            item = next((item for item in available_items if item.name == item_name), None)
            if item:
                selected_items.append(item)

        # Add situational items based on enemy composition
        for enemy_role in enemy_comp:
            counter_items = template.counter_items.get(enemy_role, [])
            for item_name in counter_items:
                item = next((item for item in available_items if item.name == item_name), None)
                if item and item not in selected_items:
                    selected_items.append(item)

        # Add power spike items if we have room
        for item_name in template.power_spike_items:
            if len(selected_items) < 6:
                item = next((item for item in available_items if item.name == item_name), None)
                if item and item not in selected_items:
                    selected_items.append(item)

        # Add late game items if we have room
        for item_name in template.late_game_items:
            if len(selected_items) < 6:
                item = next((item for item in available_items if item.name == item_name), None)
                if item and item not in selected_items:
                    selected_items.append(item)

        # Calculate total cost
        total_cost = sum(item.cost for item in selected_items)

        return Build(items=selected_items, total_cost=total_cost) if selected_items else None
