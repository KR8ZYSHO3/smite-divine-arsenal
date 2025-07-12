#!/usr/bin/env python3
"""
PostgreSQL Database Adapter for Divine Arsenal
Replaces legacy SQLite Database class with PostgreSQL compatibility
"""

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database_config import get_database_config

logger = logging.getLogger(__name__)


class PostgreSQLDatabaseAdapter:
    """
    PostgreSQL database adapter that implements the same interface as legacy Database class.
    This allows existing optimizers and systems to work with PostgreSQL without major refactoring.
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize PostgreSQL connection using database config."""
        # Ignore db_path parameter for PostgreSQL (kept for compatibility)
        self.db_config = get_database_config()
        self.engine = create_engine(self.db_config.get_database_uri())
        self.Session = sessionmaker(bind=self.engine)
        logger.info("✅ PostgreSQL database adapter initialized")

    @contextmanager
    def get_connection(self):
        """Get a database connection with proper context management."""
        session = self.Session()
        try:
            yield session
        finally:
            session.close()

    def get_all_gods(self) -> List[Dict[str, Any]]:
        """Get all gods from PostgreSQL database."""
        with self.get_connection() as session:
            try:
                result = session.execute(text("SELECT * FROM gods ORDER BY name"))
                gods = []
                for row in result:
                    god_dict = dict(row._mapping)
                    gods.append(god_dict)
                return gods
            except Exception as e:
                logger.error(f"Error fetching gods: {e}")
                return []

    def get_god(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific god by name."""
        with self.get_connection() as session:
            try:
                result = session.execute(text("SELECT * FROM gods WHERE name = :name"), {"name": name})
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return None
            except Exception as e:
                logger.error(f"Error fetching god {name}: {e}")
                return None

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items from PostgreSQL database."""
        with self.get_connection() as session:
            try:
                result = session.execute(text("SELECT * FROM items ORDER BY name"))
                items = []
                for row in result:
                    item_dict = dict(row._mapping)
                    items.append(item_dict)
                return items
            except Exception as e:
                logger.error(f"Error fetching items: {e}")
                return []

    def get_item(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific item by name."""
        with self.get_connection() as session:
            try:
                result = session.execute(text("SELECT * FROM items WHERE name = :name"), {"name": name})
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return None
            except Exception as e:
                logger.error(f"Error fetching item {name}: {e}")
                return None

    def get_patches(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get patches from PostgreSQL database."""
        with self.get_connection() as session:
            try:
                query = "SELECT * FROM patches ORDER BY created_at DESC"
                if limit:
                    query += f" LIMIT {limit}"
                result = session.execute(text(query))
                patches = []
                for row in result:
                    patch_dict = dict(row._mapping)
                    patches.append(patch_dict)
                return patches
            except Exception as e:
                logger.error(f"Error fetching patches: {e}")
                return []

    def get_patch_by_version(self, version: str) -> Optional[Dict[str, Any]]:
        """Get a specific patch by version."""
        with self.get_connection() as session:
            try:
                result = session.execute(text("SELECT * FROM patches WHERE version = :version"), {"version": version})
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return None
            except Exception as e:
                logger.error(f"Error fetching patch {version}: {e}")
                return None

    def add_god(self, god_data: Dict[str, Any]) -> int:
        """Add a god to the database."""
        with self.get_connection() as session:
            try:
                # Extract god data
                name = god_data.get('name', '')
                role = god_data.get('role', '')
                damage_type = god_data.get('damage_type', '')
                pantheon = god_data.get('pantheon', '')
                
                # Stats
                health = god_data.get('health', 0.0)
                mana = god_data.get('mana', 0.0)
                physical_power = god_data.get('physical_power', 0.0)
                magical_power = god_data.get('magical_power', 0.0)
                physical_protection = god_data.get('physical_protection', 0.0)
                magical_protection = god_data.get('magical_protection', 0.0)
                attack_speed = god_data.get('attack_speed', 0.0)
                movement_speed = god_data.get('movement_speed', 0.0)
                
                # Scaling
                health_per_level = god_data.get('health_per_level', 0.0)
                mana_per_level = god_data.get('mana_per_level', 0.0)
                physical_power_per_level = god_data.get('physical_power_per_level', 0.0)
                magical_power_per_level = god_data.get('magical_power_per_level', 0.0)
                physical_protection_per_level = god_data.get('physical_protection_per_level', 0.0)
                magical_protection_per_level = god_data.get('magical_protection_per_level', 0.0)

                insert_query = text("""
                    INSERT INTO gods (name, role, damage_type, pantheon, health, mana, physical_power, 
                                    magical_power, physical_protection, magical_protection, attack_speed, 
                                    movement_speed, health_per_level, mana_per_level, physical_power_per_level, 
                                    magical_power_per_level, physical_protection_per_level, magical_protection_per_level)
                    VALUES (:name, :role, :damage_type, :pantheon, :health, :mana, :physical_power, 
                           :magical_power, :physical_protection, :magical_protection, :attack_speed, 
                           :movement_speed, :health_per_level, :mana_per_level, :physical_power_per_level, 
                           :magical_power_per_level, :physical_protection_per_level, :magical_protection_per_level)
                    RETURNING id
                """)
                
                result = session.execute(insert_query, {
                    'name': name, 'role': role, 'damage_type': damage_type, 'pantheon': pantheon,
                    'health': health, 'mana': mana, 'physical_power': physical_power, 'magical_power': magical_power,
                    'physical_protection': physical_protection, 'magical_protection': magical_protection,
                    'attack_speed': attack_speed, 'movement_speed': movement_speed,
                    'health_per_level': health_per_level, 'mana_per_level': mana_per_level,
                    'physical_power_per_level': physical_power_per_level, 'magical_power_per_level': magical_power_per_level,
                    'physical_protection_per_level': physical_protection_per_level, 'magical_protection_per_level': magical_protection_per_level
                })
                
                row = result.fetchone()
                if row:
                    god_id = row[0]
                    session.commit()
                    return god_id
                else:
                    session.rollback()
                    return 0
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding god: {e}")
                return 0

    def add_item(self, item_data: Dict[str, Any]) -> int:
        """Add an item to the database."""
        with self.get_connection() as session:
            try:
                # Extract item data
                name = item_data.get('name', '')
                cost = item_data.get('cost', 0)
                tier = item_data.get('tier', 1)
                category = item_data.get('category', '')
                
                # Stats
                health = item_data.get('health', 0.0)
                mana = item_data.get('mana', 0.0)
                physical_power = item_data.get('physical_power', 0.0)
                magical_power = item_data.get('magical_power', 0.0)
                physical_protection = item_data.get('physical_protection', 0.0)
                magical_protection = item_data.get('magical_protection', 0.0)
                attack_speed = item_data.get('attack_speed', 0.0)
                movement_speed = item_data.get('movement_speed', 0.0)
                penetration = item_data.get('penetration', 0.0)
                critical_chance = item_data.get('critical_chance', 0.0)
                cooldown_reduction = item_data.get('cooldown_reduction', 0.0)
                lifesteal = item_data.get('lifesteal', 0.0)
                
                # Descriptions
                passive_description = item_data.get('passive_description', '')
                active_description = item_data.get('active_description', '')

                insert_query = text("""
                    INSERT INTO items (name, cost, tier, category, health, mana, physical_power, 
                                     magical_power, physical_protection, magical_protection, attack_speed, 
                                     movement_speed, penetration, critical_chance, cooldown_reduction, lifesteal,
                                     passive_description, active_description)
                    VALUES (:name, :cost, :tier, :category, :health, :mana, :physical_power, 
                           :magical_power, :physical_protection, :magical_protection, :attack_speed, 
                           :movement_speed, :penetration, :critical_chance, :cooldown_reduction, :lifesteal,
                           :passive_description, :active_description)
                    RETURNING id
                """)
                
                result = session.execute(insert_query, {
                    'name': name, 'cost': cost, 'tier': tier, 'category': category,
                    'health': health, 'mana': mana, 'physical_power': physical_power, 'magical_power': magical_power,
                    'physical_protection': physical_protection, 'magical_protection': magical_protection,
                    'attack_speed': attack_speed, 'movement_speed': movement_speed,
                    'penetration': penetration, 'critical_chance': critical_chance,
                    'cooldown_reduction': cooldown_reduction, 'lifesteal': lifesteal,
                    'passive_description': passive_description, 'active_description': active_description
                })
                
                row = result.fetchone()
                if row:
                    item_id = row[0]
                    session.commit()
                    return item_id
                else:
                    session.rollback()
                    return 0
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding item: {e}")
                return 0

    def add_patch(self, version: str, date: str, notes: str, title: str = "", url: str = "", source: str = "manual") -> int:
        """Add a patch to the database."""
        with self.get_connection() as session:
            try:
                insert_query = text("""
                    INSERT INTO patches (version, name, release_date, god_changes, item_changes, system_changes, source)
                    VALUES (:version, :name, :release_date, :god_changes, :item_changes, :system_changes, :source)
                    RETURNING id
                """)
                
                result = session.execute(insert_query, {
                    'version': version,
                    'name': title,
                    'release_date': date,
                    'god_changes': notes,  # Store all notes as god_changes for now
                    'item_changes': '',
                    'system_changes': '',
                    'source': source
                })
                
                row = result.fetchone()
                if row:
                    patch_id = row[0]
                    session.commit()
                    return patch_id
                else:
                    session.rollback()
                    return 0
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding patch: {e}")
                return 0

    def close(self):
        """Close database connection."""
        if hasattr(self, 'engine'):
            self.engine.dispose()
        logger.info("✅ PostgreSQL database adapter closed")

    # Additional methods for compatibility with legacy Database class
    def get_god_stats_history(self, god_name: str, stat_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get god stats history (placeholder for now)."""
        return []

    def add_god_stats(self, god_name: str, stats: Dict[str, float]) -> None:
        """Add god stats (placeholder for now)."""
        pass

    def import_wiki_data(self, gods_data: List[Dict], items_data: List[Dict], patches_data: List[Dict]) -> None:
        """Import wiki data in bulk."""
        logger.info(f"Importing {len(gods_data)} gods, {len(items_data)} items, {len(patches_data)} patches")
        
        # Import gods
        for god_data in gods_data:
            try:
                self.add_god(god_data)
            except Exception as e:
                logger.error(f"Error importing god {god_data.get('name', 'Unknown')}: {e}")
        
        # Import items
        for item_data in items_data:
            try:
                self.add_item(item_data)
            except Exception as e:
                logger.error(f"Error importing item {item_data.get('name', 'Unknown')}: {e}")
        
        # Import patches
        for patch_data in patches_data:
            try:
                self.add_patch(
                    patch_data.get('version', ''),
                    patch_data.get('date', ''),
                    patch_data.get('notes', ''),
                    patch_data.get('title', ''),
                    patch_data.get('url', ''),
                    patch_data.get('source', 'wiki')
                )
            except Exception as e:
                logger.error(f"Error importing patch {patch_data.get('version', 'Unknown')}: {e}")


# Create a factory function to replace legacy Database class
def create_database_adapter(db_path: Optional[str] = None) -> PostgreSQLDatabaseAdapter:
    """
    Factory function to create PostgreSQL database adapter.
    This can be used as a drop-in replacement for the legacy Database class.
    """
    return PostgreSQLDatabaseAdapter(db_path)


# For backward compatibility, create an alias
Database = PostgreSQLDatabaseAdapter 