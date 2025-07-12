#!/usr/bin/env python3
"""
Data Loader for SMITE 2 Divine Arsenal
Converts existing data files into the format needed by the build optimizer.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class DataLoader:
    """Loads and converts god and item data for the build optimizer."""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.gods_data = {}
        self.items_data = {}

    def parse_stat_string(self, stat_str: str) -> float:
        """Convert stat strings like '2 (+0)' to actual numbers."""
        if not stat_str or stat_str == "":
            return 0.0

        # Extract the base value (before the +)
        match = re.match(r'(\d+(?:\.\d+)?)', str(stat_str))
        if match:
            return float(match.group(1))
        return 0.0

    def load_gods_data(self) -> Dict[str, Any]:
        """Load and convert god data from the JSON file."""
        gods_file = self.data_dir / "gods_with_scaling.json"

        if not gods_file.exists():
            print(f"⚠️  Gods file not found: {gods_file}")
            return {}

        try:
            with open(gods_file, 'r', encoding='utf-8') as f:
                gods_raw = json.load(f)

            print(f"📊 Loading {len(gods_raw)} gods from {gods_file}")

            converted_gods = {}
            for god in gods_raw:
                name = god.get('name', 'Unknown')

                # Convert stats from string format to numbers
                stats = god.get('stats', {})
                converted_stats = {
                    'base_health': self.parse_stat_string(stats.get('health', '0')) * 100,  # Convert to actual health
                    'base_mana': self.parse_stat_string(stats.get('mana', '0')) * 100,      # Convert to actual mana
                    'base_physical_power': self.parse_stat_string(stats.get('physical_power', '0')),
                    'base_magical_power': self.parse_stat_string(stats.get('magical_power', '0')),
                    'base_physical_protection': self.parse_stat_string(stats.get('physical_protection', '0')),
                    'base_magical_protection': self.parse_stat_string(stats.get('magical_protection', '0')),
                    'base_attack_speed': self.parse_stat_string(stats.get('attack_speed', '0.9')),
                    'base_movement_speed': self.parse_stat_string(stats.get('movement_speed', '375')),
                }

                # Add per-level scaling (reasonable defaults)
                converted_stats.update({
                    'health_per_level': 85,
                    'mana_per_level': 50,
                    'physical_power_per_level': 2.0,
                    'magical_power_per_level': 0,
                    'physical_protection_per_level': 2.5,
                    'magical_protection_per_level': 1.5,
                })

                # Add ability scaling (reasonable defaults for now)
                converted_stats['ability_scaling'] = {
                    "1": 0.7,  # First ability
                    "2": 0.6,  # Second ability
                    "3": 0.5,  # Third ability
                    "4": 0.9,  # Ultimate
                }

                converted_gods[name] = converted_stats

            print(f"✅ Converted {len(converted_gods)} gods")
            return converted_gods

        except Exception as e:
            print(f"❌ Error loading gods data: {e}")
            return {}

    def load_items_data(self) -> List[Dict[str, Any]]:
        """Load and convert item data from the JSON file."""
        items_file = self.data_dir / "smite2_items_official_direct.json"

        if not items_file.exists():
            print(f"⚠️  Items file not found: {items_file}")
            return []

        try:
            with open(items_file, 'r', encoding='utf-8') as f:
                items_raw = json.load(f)

            print(f"📊 Loading {len(items_raw)} items from {items_file}")

            converted_items = []
            for item in items_raw:
                name = item.get('name', 'Unknown Item')

                # Skip items without names or with empty stats
                if not name or name == 'Unknown Item':
                    continue

                # Create reasonable stats for items (since the original stats are empty)
                # This is a temporary solution - ideally you'd have real stats
                item_stats = {
                    'name': name,
                    'cost': 2500,  # Default cost
                    'stats': {
                        'magical_power': 80 if 'magical' in name.lower() else 0,
                        'physical_power': 80 if 'physical' in name.lower() else 0,
                        'health': 200 if 'health' in name.lower() or 'shield' in name.lower() else 0,
                        'mana': 200 if 'mana' in name.lower() else 0,
                        'physical_protection': 50 if 'protection' in name.lower() else 0,
                        'magical_protection': 50 if 'protection' in name.lower() else 0,
                        'attack_speed': 0.15 if 'speed' in name.lower() else 0,
                        'movement_speed': 10 if 'movement' in name.lower() else 0,
                    }
                }

                converted_items.append(item_stats)

            print(f"✅ Converted {len(converted_items)} items")
            return converted_items

        except Exception as e:
            print(f"❌ Error loading items data: {e}")
            return []

    def get_god_stats(self, god_name: str) -> Optional[Dict[str, Any]]:
        """Get stats for a specific god."""
        if not self.gods_data:
            self.gods_data = self.load_gods_data()
        return self.gods_data.get(god_name)

    def get_all_gods(self) -> List[str]:
        """Get list of all available gods."""
        if not self.gods_data:
            self.gods_data = self.load_gods_data()
        return list(self.gods_data.keys())

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get list of all available items."""
        if not self.items_data:
            self.items_data = self.load_items_data()
        return self.items_data


# Global instance
data_loader = DataLoader()
