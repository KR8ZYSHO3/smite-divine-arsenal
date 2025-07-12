#!/usr/bin/env python3
"""
PostgreSQL Data Population Script for SMITE 2 Divine Arsenal
Populates PostgreSQL with clean SMITE 2 data
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_with_migrations import app, db, God, Item, Patch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_clean_smite2_data():
    """Populate PostgreSQL with clean SMITE 2 data."""
    
    # Clean SMITE 2 Gods Data (OB13 Authentic)
    gods_data = [
        {
            "name": "Achilles",
            "role": "Solo",
            "damage_type": "Physical",
            "pantheon": "Greek",
            "health": 610.0,
            "mana": 230.0,
            "physical_power": 39.0,
            "magical_power": 0.0,
            "physical_protection": 18.0,
            "magical_protection": 32.0,
            "attack_speed": 1.0,
            "movement_speed": 365.0,
            "health_per_level": 85.0,
            "mana_per_level": 35.0,
            "physical_power_per_level": 2.2,
            "magical_power_per_level": 0.0,
            "physical_protection_per_level": 2.9,
            "magical_protection_per_level": 0.9,
        },
        {
            "name": "Agni",
            "role": "Mid",
            "damage_type": "Magical",
            "pantheon": "Hindu",
            "health": 450.0,
            "mana": 280.0,
            "physical_power": 0.0,
            "magical_power": 36.0,
            "physical_protection": 11.0,
            "magical_protection": 32.0,
            "attack_speed": 0.87,
            "movement_speed": 365.0,
            "health_per_level": 72.0,
            "mana_per_level": 44.0,
            "physical_power_per_level": 0.0,
            "magical_power_per_level": 1.5,
            "physical_protection_per_level": 2.8,
            "magical_protection_per_level": 0.9,
        },
        {
            "name": "Anhur",
            "role": "Carry",
            "damage_type": "Physical",
            "pantheon": "Egyptian",
            "health": 470.0,
            "mana": 230.0,
            "physical_power": 38.0,
            "magical_power": 0.0,
            "physical_protection": 12.0,
            "magical_protection": 32.0,
            "attack_speed": 0.95,
            "movement_speed": 365.0,
            "health_per_level": 78.0,
            "mana_per_level": 34.0,
            "physical_power_per_level": 2.5,
            "magical_power_per_level": 0.0,
            "physical_protection_per_level": 2.9,
            "magical_protection_per_level": 0.9,
        },
        {
            "name": "Zeus",
            "role": "Mid",
            "damage_type": "Magical",
            "pantheon": "Greek",
            "health": 460.0,
            "mana": 300.0,
            "physical_power": 0.0,
            "magical_power": 43.0,
            "physical_protection": 13.0,
            "magical_protection": 32.0,
            "attack_speed": 0.91,
            "movement_speed": 365.0,
            "health_per_level": 75.0,
            "mana_per_level": 49.0,
            "physical_power_per_level": 0.0,
            "magical_power_per_level": 1.7,
            "physical_protection_per_level": 2.6,
            "magical_protection_per_level": 0.9,
        },
        {
            "name": "Hecate",
            "role": "Mid",
            "damage_type": "Magical",
            "pantheon": "Greek",
            "health": 440.0,
            "mana": 290.0,
            "physical_power": 0.0,
            "magical_power": 41.0,
            "physical_protection": 11.0,
            "magical_protection": 32.0,
            "attack_speed": 0.88,
            "movement_speed": 365.0,
            "health_per_level": 71.0,
            "mana_per_level": 47.0,
            "physical_power_per_level": 0.0,
            "magical_power_per_level": 1.6,
            "physical_protection_per_level": 2.7,
            "magical_protection_per_level": 0.9,
        },
        {
            "name": "Loki",
            "role": "Jungle",
            "damage_type": "Physical",
            "pantheon": "Norse",
            "health": 455.0,
            "mana": 240.0,
            "physical_power": 36.0,
            "magical_power": 0.0,
            "physical_protection": 12.0,
            "magical_protection": 32.0,
            "attack_speed": 0.92,
            "movement_speed": 375.0,
            "health_per_level": 73.0,
            "mana_per_level": 36.0,
            "physical_power_per_level": 2.3,
            "magical_power_per_level": 0.0,
            "physical_protection_per_level": 2.8,
            "magical_protection_per_level": 0.9,
        },
    ]

    # Clean SMITE 2 Items Data (OB13 Authentic)
    items_data = [
        {
            "name": "Jotunn's Wrath",
            "cost": 2300,
            "tier": 3,
            "category": "Physical Power",
            "health": 0.0,
            "mana": 0.0,
            "physical_power": 40.0,
            "magical_power": 0.0,
            "physical_protection": 0.0,
            "magical_protection": 0.0,
            "attack_speed": 0.0,
            "movement_speed": 0.0,
            "penetration": 10.0,
            "critical_chance": 0.0,
            "cooldown_reduction": 20.0,
            "lifesteal": 0.0,
            "passive_description": "Provides physical power and cooldown reduction",
            "active_description": "",
        },
        {
            "name": "Deathbringer",
            "cost": 3000,
            "tier": 3,
            "category": "Physical Power",
            "health": 0.0,
            "mana": 0.0,
            "physical_power": 50.0,
            "magical_power": 0.0,
            "physical_protection": 0.0,
            "magical_protection": 0.0,
            "attack_speed": 0.0,
            "movement_speed": 0.0,
            "penetration": 0.0,
            "critical_chance": 25.0,
            "cooldown_reduction": 0.0,
            "lifesteal": 0.0,
            "passive_description": "Critical hits deal 25% more damage",
            "active_description": "",
        },
        {
            "name": "Book of Thoth",
            "cost": 2300,
            "tier": 3,
            "category": "Magical Power",
            "health": 0.0,
            "mana": 125.0,
            "physical_power": 0.0,
            "magical_power": 80.0,
            "physical_protection": 0.0,
            "magical_protection": 0.0,
            "attack_speed": 0.0,
            "movement_speed": 0.0,
            "penetration": 0.0,
            "critical_chance": 0.0,
            "cooldown_reduction": 0.0,
            "lifesteal": 0.0,
            "passive_description": "Gain magical power based on maximum mana",
            "active_description": "",
        },
        {
            "name": "Rod of Tahuti",
            "cost": 3000,
            "tier": 3,
            "category": "Magical Power",
            "health": 0.0,
            "mana": 0.0,
            "physical_power": 0.0,
            "magical_power": 120.0,
            "physical_protection": 0.0,
            "magical_protection": 0.0,
            "attack_speed": 0.0,
            "movement_speed": 0.0,
            "penetration": 0.0,
            "critical_chance": 0.0,
            "cooldown_reduction": 0.0,
            "lifesteal": 0.0,
            "passive_description": "Increases magical power by 25% when enemies are below 50% health",
            "active_description": "",
        },
        {
            "name": "Sovereignty",
            "cost": 2100,
            "tier": 3,
            "category": "Defense",
            "health": 300.0,
            "mana": 0.0,
            "physical_power": 0.0,
            "magical_power": 0.0,
            "physical_protection": 60.0,
            "magical_protection": 0.0,
            "attack_speed": 0.0,
            "movement_speed": 0.0,
            "penetration": 0.0,
            "critical_chance": 0.0,
            "cooldown_reduction": 0.0,
            "lifesteal": 0.0,
            "passive_description": "Aura: Allies gain 20 physical protection",
            "active_description": "",
        },
        {
            "name": "Heartward Amulet",
            "cost": 2100,
            "tier": 3,
            "category": "Defense",
            "health": 250.0,
            "mana": 0.0,
            "physical_power": 0.0,
            "magical_power": 0.0,
            "physical_protection": 0.0,
            "magical_protection": 60.0,
            "attack_speed": 0.0,
            "movement_speed": 0.0,
            "penetration": 0.0,
            "critical_chance": 0.0,
            "cooldown_reduction": 0.0,
            "lifesteal": 0.0,
            "passive_description": "Aura: Allies gain 20 magical protection",
            "active_description": "",
        },
    ]

    try:
        with app.app_context():
            # Clear existing data
            logger.info("🧹 Clearing existing data...")
            db.session.query(God).delete()
            db.session.query(Item).delete()
            db.session.query(Patch).delete()
            db.session.commit()
            
            # Add gods
            logger.info("👥 Adding gods...")
            for god_data in gods_data:
                god = God(**god_data)
                db.session.add(god)
                logger.info(f"  ✅ Added {god_data['name']} ({god_data['role']})")
            
            # Add items
            logger.info("⚔️ Adding items...")
            for item_data in items_data:
                item = Item(**item_data)
                db.session.add(item)
                logger.info(f"  ✅ Added {item_data['name']} ({item_data['cost']}g)")
            
            # Commit all changes
            db.session.commit()
            
            # Verify data
            gods_count = db.session.query(God).count()
            items_count = db.session.query(Item).count()
            
            logger.info(f"🎉 Database populated successfully!")
            logger.info(f"   Gods: {gods_count}")
            logger.info(f"   Items: {items_count}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error populating database: {e}")
        db.session.rollback()
        return False


def main():
    """Main function to populate the database."""
    print("🗄️ SMITE 2 DIVINE ARSENAL - PostgreSQL Data Population")
    print("=" * 65)
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not set!")
        print("   Set it before running this script.")
        return
    
    print(f"🔗 Database: PostgreSQL")
    print(f"🌐 URL: {os.getenv('DATABASE_URL', '').split('@')[0]}@***")
    print()
    
    # Populate data
    if populate_clean_smite2_data():
        print("🎉 Data population completed successfully!")
    else:
        print("❌ Data population failed!")


if __name__ == "__main__":
    main() 