"""Database setup and operations for Divine Arsenal."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional


class Database:
    """Handles database operations for Divine Arsenal."""

    def __init__(self, db_path: str = "divine_arsenal.db") -> None:
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Get a database connection with proper context management.

        Yields:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create gods table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS gods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL,
                    damage_type TEXT NOT NULL,
                    pantheon TEXT,
                    type TEXT,
                    health REAL,
                    mana REAL,
                    physical_power REAL,
                    magical_power REAL,
                    physical_protection REAL,
                    magical_protection REAL,
                    attack_speed REAL,
                    movement_speed REAL,
                    speed REAL,
                    range_val REAL,
                    intelligence TEXT,
                    strength TEXT,
                    scaling_info TEXT,
                    lore TEXT,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create god_abilities table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS god_abilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    god_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    ability_type TEXT,
                    scaling_physical_power REAL DEFAULT 0,
                    scaling_magical_power REAL DEFAULT 0,
                    cooldown REAL DEFAULT 0,
                    FOREIGN KEY (god_id) REFERENCES gods (id) ON DELETE CASCADE
                )
            """
            )

            # Create god_relationships table (counters, strong against, etc.)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS god_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    god_id INTEGER NOT NULL,
                    related_god_name TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    FOREIGN KEY (god_id) REFERENCES gods (id) ON DELETE CASCADE
                )
            """
            )

            # Create god_playstyles table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS god_playstyles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    god_id INTEGER NOT NULL,
                    playstyle TEXT NOT NULL,
                    FOREIGN KEY (god_id) REFERENCES gods (id) ON DELETE CASCADE
                )
            """
            )

            # Create items table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT,
                    tier TEXT,
                    cost INTEGER,
                    category TEXT,
                    description TEXT,
                    passive TEXT,
                    active TEXT,
                    physical_power REAL DEFAULT 0,
                    magical_power REAL DEFAULT 0,
                    physical_protection REAL DEFAULT 0,
                    magical_protection REAL DEFAULT 0,
                    health REAL DEFAULT 0,
                    mana REAL DEFAULT 0,
                    movement_speed REAL DEFAULT 0,
                    attack_speed REAL DEFAULT 0,
                    cooldown_reduction REAL DEFAULT 0,
                    penetration REAL DEFAULT 0,
                    lifesteal REAL DEFAULT 0,
                    crit_chance REAL DEFAULT 0,
                    crit_damage REAL DEFAULT 0,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create item_tags table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS item_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
                )
            """
            )

            # Create item_stats table (for dynamic stats that don't fit in main table)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS item_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    stat_name TEXT NOT NULL,
                    stat_value REAL NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
                )
            """
            )

            # Create patches table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS patches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL,
                    title TEXT,
                    date TEXT NOT NULL,
                    content TEXT NOT NULL,
                    url TEXT,
                    source TEXT DEFAULT 'wiki',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create stats_history table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stats_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    god_name TEXT NOT NULL,
                    stat_name TEXT NOT NULL,
                    stat_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(god_name, stat_name, timestamp)
                )
            """
            )

            # Create builds table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS builds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    god_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    total_cost REAL NOT NULL,
                    win_rate REAL DEFAULT 0,
                    popularity REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create build_items table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS build_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    build_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    slot_order INTEGER DEFAULT 0,
                    FOREIGN KEY (build_id) REFERENCES builds (id) ON DELETE CASCADE
                )
            """
            )

            # Create build_stats table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS build_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    build_id INTEGER NOT NULL,
                    stat_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    FOREIGN KEY (build_id) REFERENCES builds (id) ON DELETE CASCADE
                )
            """
            )

            # Create indexes for better performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_stats_history_god
                ON stats_history(god_name, timestamp)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_gods_role
                ON gods(role)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_gods_damage_type
                ON gods(damage_type)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_items_category
                ON items(category)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_items_tier
                ON items(tier)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_patches_version
                ON patches(version)
            """
            )

            conn.commit()

    def add_patch(
        self,
        version: str,
        date: str,
        notes: str,
        title: str = "",
        url: str = "",
        source: str = "manual",
    ) -> int:
        """Add a new patch to the database.

        Args:
            version: The patch version number
            date: The patch release date
            notes: The patch notes content
            title: The patch title (optional)
            url: URL to the patch notes (optional)
            source: Source of the patch data (optional)

        Returns:
            The ID of the newly inserted patch
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO patches (version, title, date, content, url, source) VALUES (?, ?, ?, ?, ?, ?)",
                (version, title, date, notes, url, source),
            )
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid is not None else 0

    def add_god_stats(self, god_name: str, stats: Dict[str, float]) -> None:
        """Add god statistics to the history.

        Args:
            god_name: Name of the god
            stats: Dictionary of stat names and values
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()

            for stat_name, value in stats.items():
                cursor.execute(
                    """
                    INSERT INTO stats_history (god_name, stat_name, stat_value, timestamp)
                    VALUES (?, ?, ?, ?)
                """,
                    (god_name, stat_name, value, timestamp),
                )

            conn.commit()

    def get_god_stats_history(
        self, god_name: str, stat_name: str, days: int = 30
    ) -> List[Dict[str, str]]:
        """Get historical statistics for a specific god and stat.

        Args:
            god_name: Name of the god
            stat_name: Name of the stat to retrieve
            days: Number of days of history to return

        Returns:
            List of dictionaries containing historical stat values
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT stat_value, timestamp
                FROM stats_history
                WHERE god_name = ? AND stat_name = ?
                AND timestamp >= datetime('now', ?)
                ORDER BY timestamp DESC
            """,
                (god_name, stat_name, f"-{days} days"),
            )

            return [{"value": row[0], "timestamp": row[1]} for row in cursor.fetchall()]

    def get_patches(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Retrieve patches from the database.

        Args:
            limit: Optional limit on number of patches to return

        Returns:
            List of dictionaries containing patch information
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM patches ORDER BY date DESC"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query)

            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_patch_by_version(self, version: str) -> Optional[Dict[str, str]]:
        """Retrieve a specific patch by version number.

        Args:
            version: The patch version to look up

        Returns:
            Dictionary containing patch information or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patches WHERE version = ?", (version,))
            row = cursor.fetchone()

            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    def add_god(self, god_data: Dict[str, Any]) -> int:
        """Add or update a god in the database.

        Args:
            god_data: Dictionary containing god information

        Returns:
            The ID of the god record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Insert or update god
            cursor.execute(
                """
                INSERT OR REPLACE INTO gods (
                    name, role, damage_type, pantheon, type,
                    health, mana, physical_power, magical_power,
                    physical_protection, magical_protection,
                    attack_speed, movement_speed, speed, range_val, 
                    intelligence, strength, scaling_info, lore, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    god_data.get("name", ""),
                    god_data.get("role", ""),
                    god_data.get("damage_type", ""),
                    god_data.get("pantheon", ""),
                    god_data.get("type", ""),
                    god_data.get("health", 0),
                    god_data.get("mana", 0),
                    god_data.get("physical_power", 0),
                    god_data.get("magical_power", 0),
                    god_data.get("physical_protection", 0),
                    god_data.get("magical_protection", 0),
                    god_data.get("attack_speed", 0),
                    god_data.get("movement_speed", 0),
                    god_data.get("speed", 0),
                    god_data.get("range_val", 0),
                    god_data.get("intelligence", ""),
                    god_data.get("strength", ""),
                    god_data.get("scaling_info", ""),
                    god_data.get("lore", ""),
                    god_data.get("image_url", ""),
                ),
            )

            god_id = (
                cursor.lastrowid
                or cursor.execute(
                    "SELECT id FROM gods WHERE name = ?", (god_data.get("name"),)
                ).fetchone()[0]
            )

            # Clear existing abilities and relationships
            cursor.execute("DELETE FROM god_abilities WHERE god_id = ?", (god_id,))
            cursor.execute("DELETE FROM god_relationships WHERE god_id = ?", (god_id,))
            cursor.execute("DELETE FROM god_playstyles WHERE god_id = ?", (god_id,))

            # Add abilities
            if "abilities" in god_data and isinstance(god_data["abilities"], list):
                for ability in god_data["abilities"]:
                    if isinstance(ability, dict):
                        cursor.execute(
                            """
                            INSERT INTO god_abilities (god_id, name, description, ability_type)
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                god_id,
                                ability.get("name", ""),
                                ability.get("description", ""),
                                ability.get("type", ""),
                            ),
                        )

            # Add relationships (counter_gods, strong_against, weak_against)
            for relationship_type in ["counter_gods", "strong_against", "weak_against"]:
                if relationship_type in god_data and isinstance(god_data[relationship_type], list):
                    for related_god in god_data[relationship_type]:
                        cursor.execute(
                            """
                            INSERT INTO god_relationships (god_id, related_god_name, relationship_type)
                            VALUES (?, ?, ?)
                            """,
                            (god_id, related_god, relationship_type),
                        )

            # Add playstyles
            if "playstyle" in god_data and isinstance(god_data["playstyle"], list):
                for style in god_data["playstyle"]:
                    cursor.execute(
                        """
                        INSERT INTO god_playstyles (god_id, playstyle)
                        VALUES (?, ?)
                        """,
                        (god_id, style),
                    )

            conn.commit()
            return god_id

    def get_god(self, name: str) -> Optional[Dict[str, Any]]:
        """Get god data by name.

        Args:
            name: Name of the god

        Returns:
            Dictionary containing god data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get basic god data
            cursor.execute("SELECT * FROM gods WHERE name = ?", (name,))
            row = cursor.fetchone()

            if not row:
                return None

            columns = [description[0] for description in cursor.description]
            god_data = dict(zip(columns, row))
            god_id = god_data["id"]

            # Parse scaling_info if present
            if god_data.get("scaling_info"):
                try:
                    import json

                    god_data["scaling_info"] = json.loads(god_data["scaling_info"])
                except (json.JSONDecodeError, TypeError):
                    god_data["scaling_info"] = {}

            # Create stats dictionary with scaling data
            god_data["stats"] = {
                "health": god_data.get("health", 0),
                "mana": god_data.get("mana", 0),
                "physical_power": god_data.get("physical_power", 0),
                "magical_power": god_data.get("magical_power", 0),
                "physical_protection": god_data.get("physical_protection", 0),
                "magical_protection": god_data.get("magical_protection", 0),
                "attack_speed": god_data.get("attack_speed", 0),
                "movement_speed": god_data.get("movement_speed", 0),
                "intelligence": god_data.get("intelligence", ""),
                "strength": god_data.get("strength", ""),
            }

            # Get abilities
            cursor.execute(
                "SELECT name, description, ability_type FROM god_abilities WHERE god_id = ?",
                (god_id,),
            )
            god_data["abilities"] = [
                {"name": row[0], "description": row[1], "type": row[2]} for row in cursor.fetchall()
            ]

            # Get relationships
            for relationship_type in ["counter_gods", "strong_against", "weak_against"]:
                cursor.execute(
                    "SELECT related_god_name FROM god_relationships WHERE god_id = ? AND relationship_type = ?",
                    (god_id, relationship_type),
                )
                god_data[relationship_type] = [row[0] for row in cursor.fetchall()]

            # Get playstyles
            cursor.execute("SELECT playstyle FROM god_playstyles WHERE god_id = ?", (god_id,))
            god_data["playstyle"] = [row[0] for row in cursor.fetchall()]

            return god_data

    def get_all_gods(self) -> List[Dict[str, Any]]:
        """Get all gods from the database.

        Returns:
            List of dictionaries containing god data
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM gods ORDER BY name")
            god_names = [row[0] for row in cursor.fetchall()]

            gods = []
            for name in god_names:
                god = self.get_god(name)
                if god is not None:
                    gods.append(god)
            return gods

    def add_item(self, item_data: Dict[str, Any]) -> int:
        """Add or update an item in the database.

        Args:
            item_data: Dictionary containing item information

        Returns:
            The ID of the item record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Extract stats from nested dict if present, handle JSON strings
            stats_raw = item_data.get("stats", {})
            if isinstance(stats_raw, str):
                try:
                    import json

                    stats = json.loads(stats_raw)
                except (json.JSONDecodeError, TypeError):
                    stats = {}
            else:
                stats = stats_raw if isinstance(stats_raw, dict) else {}

            # Insert or update item
            cursor.execute(
                """
                INSERT OR REPLACE INTO items (
                    name, type, tier, cost, category, description, passive, active,
                    physical_power, magical_power, physical_protection, magical_protection,
                    health, mana, movement_speed, attack_speed, cooldown_reduction,
                    penetration, lifesteal, crit_chance, crit_damage, image_url, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    item_data.get("name", ""),
                    item_data.get("type", ""),
                    item_data.get("tier", ""),
                    item_data.get("cost", 0),
                    item_data.get("category", ""),
                    item_data.get("description", ""),
                    item_data.get("passive", ""),
                    item_data.get("active", ""),
                    stats.get("physical_power", 0),
                    stats.get("magical_power", 0),
                    stats.get("physical_protection", 0),
                    stats.get("magical_protection", 0),
                    stats.get("health", 0),
                    stats.get("mana", 0),
                    stats.get("movement_speed", 0),
                    stats.get("attack_speed", 0),
                    stats.get("cooldown_reduction", 0),
                    stats.get("penetration", 0),
                    stats.get("lifesteal", 0),
                    stats.get("crit_chance", 0),
                    stats.get("crit_damage", 0),
                    item_data.get("image_url", ""),
                ),
            )

            item_id = (
                cursor.lastrowid
                or cursor.execute(
                    "SELECT id FROM items WHERE name = ?", (item_data.get("name"),)
                ).fetchone()[0]
            )

            # Clear existing tags and dynamic stats
            cursor.execute("DELETE FROM item_tags WHERE item_id = ?", (item_id,))
            cursor.execute("DELETE FROM item_stats WHERE item_id = ?", (item_id,))

            # Add tags - handle JSON strings
            tags_raw = item_data.get("tags", [])
            if isinstance(tags_raw, str):
                try:
                    import json

                    tags = json.loads(tags_raw)
                except (json.JSONDecodeError, TypeError):
                    tags = []
            else:
                tags = tags_raw if isinstance(tags_raw, list) else []

            for tag in tags:
                cursor.execute("INSERT INTO item_tags (item_id, tag) VALUES (?, ?)", (item_id, tag))

            # Add any additional stats that don't fit in main table
            for stat_name, stat_value in stats.items():
                if stat_name not in [
                    "physical_power",
                    "magical_power",
                    "physical_protection",
                    "magical_protection",
                    "health",
                    "mana",
                    "movement_speed",
                    "attack_speed",
                    "cooldown_reduction",
                    "penetration",
                    "lifesteal",
                    "crit_chance",
                    "crit_damage",
                ]:
                    cursor.execute(
                        "INSERT INTO item_stats (item_id, stat_name, stat_value) VALUES (?, ?, ?)",
                        (item_id, stat_name, stat_value),
                    )

            conn.commit()
            return item_id

    def get_item(self, name: str) -> Optional[Dict[str, Any]]:
        """Get item data by name.

        Args:
            name: Name of the item

        Returns:
            Dictionary containing item data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get basic item data
            cursor.execute("SELECT * FROM items WHERE name = ?", (name,))
            row = cursor.fetchone()

            if not row:
                return None

            columns = [description[0] for description in cursor.description]
            item_data = dict(zip(columns, row))
            item_id = item_data["id"]

            # Build stats dictionary
            stats = {}
            for stat in [
                "physical_power",
                "magical_power",
                "physical_protection",
                "magical_protection",
                "health",
                "mana",
                "movement_speed",
                "attack_speed",
                "cooldown_reduction",
                "penetration",
                "lifesteal",
                "crit_chance",
                "crit_damage",
            ]:
                if item_data.get(stat, 0) != 0:
                    stats[stat] = item_data[stat]

            # Get additional stats
            cursor.execute(
                "SELECT stat_name, stat_value FROM item_stats WHERE item_id = ?", (item_id,)
            )
            for stat_name, stat_value in cursor.fetchall():
                stats[stat_name] = stat_value

            item_data["stats"] = stats

            # Get tags
            cursor.execute("SELECT tag FROM item_tags WHERE item_id = ?", (item_id,))
            item_data["tags"] = [row[0] for row in cursor.fetchall()]

            return item_data

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items from the database.

        Returns:
            List of dictionaries containing item data
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM items ORDER BY name")
            item_names = [row[0] for row in cursor.fetchall()]

            items = []
            for name in item_names:
                item = self.get_item(name)
                if item is not None:
                    items.append(item)
            return items

    def import_wiki_data(
        self, gods_data: List[Dict], items_data: List[Dict], patches_data: List[Dict]
    ) -> None:
        """Import data from wiki scraper.

        Args:
            gods_data: List of god dictionaries from wiki scraper
            items_data: List of item dictionaries from wiki scraper
            patches_data: List of patch dictionaries from wiki scraper
        """
        # Import gods
        for god_data in gods_data:
            self.add_god(god_data)

        # Import items
        for item_data in items_data:
            self.add_item(item_data)

        # Import patches
        for patch_data in patches_data:
            self.add_patch(
                version=patch_data.get("version", ""),
                date=patch_data.get("date", ""),
                notes=patch_data.get("content", ""),
                title=patch_data.get("title", ""),
                url=patch_data.get("url", ""),
                source="wiki",
            )

    def add_patch_enhanced(
        self,
        version: str,
        date: str,
        notes: str,
        title: str = "",
        url: str = "",
        source: str = "manual",
    ) -> int:
        """Add a new patch with enhanced metadata.

        Args:
            version: The patch version number
            date: The patch release date
            notes: The patch notes content
            title: The patch title
            url: URL to the patch notes
            source: Source of the patch data

        Returns:
            The ID of the newly inserted patch
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO patches (version, title, date, content, url, source) VALUES (?, ?, ?, ?, ?, ?)",
                (version, title, date, notes, url, source),
            )
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid is not None else 0
