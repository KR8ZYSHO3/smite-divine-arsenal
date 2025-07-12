"""God data access layer for Divine Arsenal build optimizer."""

from typing import Any, Dict, List, Optional

from divine_arsenal.backend.database import Database


class GodData:
    """Manages god data for the build optimizer."""

    def __init__(self, db: Database):
        self.db = db
        self._gods_cache: Optional[List[Dict[str, Any]]] = None

    def get_all_gods(self) -> List[Dict[str, Any]]:
        """Get all gods from the database."""
        if self._gods_cache is None:
            self._gods_cache = self.db.get_all_gods()
        return self._gods_cache

    def get_god(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific god by name."""
        gods = self.get_all_gods()
        for god in gods:
            if god.get("name", "").lower() == name.lower():
                return god
        return None

    def get_gods_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Get all gods for a specific role (supports combined roles like 'SoloJungle')."""
        gods = self.get_all_gods()
        return [god for god in gods if role.lower() in god.get("role", "").lower()]

    def get_gods_by_damage_type(self, damage_type: str) -> List[Dict[str, Any]]:
        """Get all gods for a specific damage type."""
        gods = self.get_all_gods()
        return [god for god in gods if god.get("damage_type", "").lower() == damage_type.lower()]

    def get_god_stats_at_level(self, god: Dict[str, Any], level: int) -> Dict[str, float]:
        """Calculate god stats at a specific level using Smite 2 scaling format."""
        stats = god.get("stats", {})
        scaling_info = god.get("scaling_info", {})

        result = {}

        # Parse stats that have scaling format like "1.7 (+0.2)"
        for stat_name, stat_value in stats.items():
            if isinstance(stat_value, str) and "(" in stat_value:
                # Parse format like "1.7 (+0.2)" or "375 (+0)"
                try:
                    base_part = stat_value.split("(")[0].strip()
                    scaling_part = stat_value.split("(")[1].split(")")[0].strip()

                    # Remove the '+' sign and convert to float
                    base_value = float(base_part)
                    scaling_value = float(scaling_part.replace("+", "").replace("-", "-"))

                    # Calculate value at level
                    level_value = base_value + (scaling_value * (level - 1))
                    result[stat_name] = level_value
                except (ValueError, IndexError):
                    # If parsing fails, try to convert directly to float
                    try:
                        result[stat_name] = float(stat_value)
                    except ValueError:
                        result[stat_name] = 0.0
            else:
                # Handle non-scaling stats
                try:
                    result[stat_name] = float(stat_value) if stat_value else 0.0
                except (ValueError, TypeError):
                    result[stat_name] = 0.0

        return result

    def get_god_scaling_info(self, god: Dict[str, Any]) -> Dict[str, Any]:
        """Get scaling information for a god."""
        return god.get("scaling_info", {})

    def get_god_roles(self, god: Dict[str, Any]) -> List[str]:
        """Get all roles for a god (handles combined roles like 'SoloJungle')."""
        role = god.get("role", "")
        if not role:
            return []

        # Split combined roles (e.g., 'SoloJungle' -> ['Solo', 'Jungle'])
        # Common role combinations in Smite 2
        role_mappings = {
            "SoloJungle": ["Solo", "Jungle"],
            "MidJungle": ["Mid", "Jungle"],
            "MidSupport": ["Mid", "Support"],
            "SupportSolo": ["Support", "Solo"],
            "MidCarry": ["Mid", "Carry"],
        }

        if role in role_mappings:
            return role_mappings[role]
        else:
            return [role]

    def get_god_meta_role(self, god: Dict[str, Any]) -> str:
        """Get the primary meta role for a god."""
        return god.get("meta_role", god.get("role", ""))

    def get_god_image_url(self, god: Dict[str, Any]) -> str:
        """Get the image URL for a god."""
        return god.get("image_url", "")

    def get_god_counter_gods(self, god: Dict[str, Any]) -> List[str]:
        """Get counter gods for a specific god."""
        return god.get("counter_gods", [])

    def get_god_counter_items(self, god: Dict[str, Any]) -> List[str]:
        """Get counter items for a specific god."""
        return god.get("counter_items", [])

    def get_god_synergy_items(self, god: Dict[str, Any]) -> List[str]:
        """Get synergy items for a specific god."""
        return god.get("synergy_items", [])

    def refresh_cache(self) -> None:
        """Refresh the gods cache."""
        self._gods_cache = None
