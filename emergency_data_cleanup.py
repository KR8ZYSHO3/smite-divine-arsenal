#!/usr/bin/env python3
"""
🚨 EMERGENCY DATA CLEANUP SCRIPT
Aggressive cleanup to fix contaminated database data
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import database configuration
try:
    from divine_arsenal.backend.database_config import get_database_config
except ImportError:
    logger.error("Could not import database config. Make sure you're running from the project root.")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)

# Load database configuration
db_config = get_database_config()
flask_config = db_config.get_flask_config()

# Apply configuration to Flask app
for key, value in flask_config.items():
    app.config[key] = value

# Additional Flask configuration
app.config.update({
    'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
    'JSON_SORT_KEYS': False,
    'PROPAGATE_EXCEPTIONS': True,
})

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models (same as in app_with_migrations.py)
class God(db.Model):
    """God model for SQLAlchemy."""
    __tablename__ = 'gods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(50))
    damage_type = db.Column(db.String(20))
    pantheon = db.Column(db.String(50))

    # Stats
    health = db.Column(db.Float, default=0.0)
    mana = db.Column(db.Float, default=0.0)
    physical_power = db.Column(db.Float, default=0.0)
    magical_power = db.Column(db.Float, default=0.0)
    physical_protection = db.Column(db.Float, default=0.0)
    magical_protection = db.Column(db.Float, default=0.0)
    attack_speed = db.Column(db.Float, default=0.0)
    movement_speed = db.Column(db.Float, default=0.0)

    # Scaling
    health_per_level = db.Column(db.Float, default=0.0)
    mana_per_level = db.Column(db.Float, default=0.0)
    physical_power_per_level = db.Column(db.Float, default=0.0)
    magical_power_per_level = db.Column(db.Float, default=0.0)
    physical_protection_per_level = db.Column(db.Float, default=0.0)
    magical_protection_per_level = db.Column(db.Float, default=0.0)

    # Metadata
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Item(db.Model):
    """Item model for SQLAlchemy."""
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    cost = db.Column(db.Integer, default=0)
    tier = db.Column(db.Integer, default=1)
    category = db.Column(db.String(50))

    # Stats
    health = db.Column(db.Float, default=0.0)
    mana = db.Column(db.Float, default=0.0)
    physical_power = db.Column(db.Float, default=0.0)
    magical_power = db.Column(db.Float, default=0.0)
    physical_protection = db.Column(db.Float, default=0.0)
    magical_protection = db.Column(db.Float, default=0.0)
    attack_speed = db.Column(db.Float, default=0.0)
    movement_speed = db.Column(db.Float, default=0.0)
    penetration = db.Column(db.Float, default=0.0)
    critical_chance = db.Column(db.Float, default=0.0)
    cooldown_reduction = db.Column(db.Float, default=0.0)
    lifesteal = db.Column(db.Float, default=0.0)

    # Descriptions
    passive_description = db.Column(db.Text)
    active_description = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# SMITE 2 OB13 Gods List (confirmed current roster)
SMITE2_GODS = [
    "Achilles", "Agni", "Ah Muzen Cab", "Ah Puch", "Aladdin", "Amaterasu", "Anhur", "Anubis", 
    "Aphrodite", "Apollo", "Athena", "Awilix", "Bacchus", "Bellona", "Cerberus", "Chaac", 
    "Fenrir", "Ganesha", "Guan Yu", "Hades", "Hun Batz", "Izanami", "Kali", "Loki", 
    "Merlin", "Neith", "Nu Wa", "Pele", "Princess Bari", "Sobek", "Vulcan", "Ymir", "Zeus"
]

# SMITE 2 OB13 Items List (confirmed current items)
SMITE2_ITEMS = [
    # Starter Items
    "Warrior's Axe", "Assassin's Blessing", "Hunter's Blessing", "Mage's Blessing", "Guardian's Blessing",
    "Conduit Gem", "Death's Toll", "Bluestone Pendant", "Vampiric Shroud", "Warding Sigil",
    
    # Physical Power Items
    "Light Blade", "Heavy Blade", "Serrated Blade", "Cursed Blade", "Poisoned Blade",
    "Balanced Blade", "Berserker's Shield", "Stone Cutting Sword", "Brawler's Beat Stick",
    "Jotunn's Wrath", "Hydra's Lament", "The Crusher", "Titan's Bane", "Heartseeker",
    "Deathbringer", "Malice", "Rage", "Wind Demon", "Poisoned Star", "Shadowsteel Shuriken",
    
    # Magical Power Items
    "Dreamer's Idol", "Polynomicon", "Bancroft's Talon", "Typhon's Fang", "Book of Thoth",
    "Doom Orb", "Soul Reaver", "Obsidian Shard", "Spear of Desolation", "Spear of the Magus",
    "Chronos' Pendant", "Breastplate of Valor", "Mantle of Discord", "Rod of Tahuti",
    "Cosmic Horror", "Necronomicon", "Prisms",
    
    # Protection Items
    "Iron Mail", "Celestial Legion Helm", "Runic Shield", "Gauntlet of Thebes", "Sovereignty",
    "Mystical Mail", "Midgardian Mail", "Emperor's Armor", "Pestilence", "Heartward Amulet",
    "Genji's Guard", "Oni Hunter's Garb", "Talisman of Energy", "Spirit Robe", "Mantle of Discord",
    "Hide of the Nemean Lion", "Magi's Cloak", "Ancile",
    
    # Utility Items
    "Meditation Cloak", "Purification Beads", "Aegis Amulet", "Blink Rune", "Phantom Veil",
    "Horrific Emblem", "Magic Shell", "Cursed Ankh", "Sunder", "Frenzy"
]

# Additional contaminated items we found in the tests
CONTAMINATED_ITEMS = [
    "Aphrodite voicelines", "Soul Piercer Achilles voicelines", "Oracle Staff", "Rod Of Asclepius",
    "Killing Stone", "Gladiator's Shield", "Hecate"  # This is actually a god, not an item
]

class EmergencyDataCleaner:
    """Emergency data cleanup operations."""
    
    def __init__(self):
        self.gods_moved = 0
        self.items_removed = 0
        self.duplicates_removed = 0
        self.contaminated_removed = 0
        
    def nuclear_cleanup(self):
        """Nuclear option - remove all contaminated data and start fresh."""
        logger.info("🚨 NUCLEAR CLEANUP - Removing ALL contaminated data")
        
        with app.app_context():
            # Delete all items that are not in the official SMITE 2 items list
            all_items = db.session.query(Item).all()
            
            for item in all_items:
                if item.name not in SMITE2_ITEMS:
                    logger.info(f"❌ REMOVING CONTAMINATED ITEM: {item.name}")
                    db.session.delete(item)
                    self.contaminated_removed += 1
            
            # Move any gods that might be in the items table
            contaminated_gods = db.session.query(Item).filter(Item.name.in_(SMITE2_GODS)).all()
            
            for item in contaminated_gods:
                # Check if god already exists
                existing_god = db.session.query(God).filter_by(name=item.name).first()
                
                if not existing_god:
                    # Create new god record
                    god = God()
                    god.name = item.name
                    god.role = "Mid"  # Default role
                    god.damage_type = "Magical"
                    god.pantheon = "Unknown"
                    
                    db.session.add(god)
                    self.gods_moved += 1
                    logger.info(f"✅ MOVED GOD: {item.name} from items to gods")
                
                # Remove from items table
                db.session.delete(item)
                self.contaminated_removed += 1
            
            # Ensure we have all SMITE 2 gods
            for god_name in SMITE2_GODS:
                existing_god = db.session.query(God).filter_by(name=god_name).first()
                if not existing_god:
                    god = God()
                    god.name = god_name
                    god.role = "Mid"  # Default role
                    god.damage_type = "Magical"
                    god.pantheon = "Unknown"
                    
                    db.session.add(god)
                    self.gods_moved += 1
                    logger.info(f"✅ ADDED MISSING GOD: {god_name}")
            
            # Remove duplicate gods
            god_names = {}
            all_gods = db.session.query(God).all()
            
            for god in all_gods:
                if god.name in god_names:
                    # This is a duplicate
                    db.session.delete(god)
                    self.duplicates_removed += 1
                    logger.info(f"❌ REMOVED DUPLICATE GOD: {god.name}")
                else:
                    god_names[god.name] = god
            
            # Add essential SMITE 2 items if missing
            essential_items = [
                {"name": "Book of Thoth", "cost": 2600, "tier": 3, "category": "Magical Power", "magical_power": 100, "mana": 125},
                {"name": "Rod of Tahuti", "cost": 3000, "tier": 3, "category": "Magical Power", "magical_power": 140},
                {"name": "Jotunn's Wrath", "cost": 2300, "tier": 3, "category": "Physical Power", "physical_power": 40, "cooldown_reduction": 20},
                {"name": "Deathbringer", "cost": 3000, "tier": 3, "category": "Physical Power", "physical_power": 50, "critical_chance": 20},
                {"name": "Gauntlet of Thebes", "cost": 2150, "tier": 3, "category": "Protection", "health": 250, "physical_protection": 45},
                {"name": "Stone Cutting Sword", "cost": 2150, "tier": 3, "category": "Physical Power", "physical_power": 40, "health": 150},
                {"name": "Bancroft's Talon", "cost": 2500, "tier": 3, "category": "Magical Power", "magical_power": 100, "lifesteal": 15},
                {"name": "Spirit Robe", "cost": 2150, "tier": 3, "category": "Protection", "physical_protection": 40, "magical_protection": 40},
                {"name": "Chronos' Pendant", "cost": 2600, "tier": 3, "category": "Magical Power", "magical_power": 80, "cooldown_reduction": 20},
                {"name": "Hide of the Nemean Lion", "cost": 2300, "tier": 3, "category": "Protection", "physical_protection": 70, "health": 200},
            ]
            
            for item_data in essential_items:
                existing_item = db.session.query(Item).filter_by(name=item_data["name"]).first()
                if not existing_item:
                    item = Item()
                    item.name = item_data["name"]
                    item.cost = item_data["cost"]
                    item.tier = item_data["tier"]
                    item.category = item_data["category"]
                    item.magical_power = item_data.get("magical_power", 0)
                    item.physical_power = item_data.get("physical_power", 0)
                    item.health = item_data.get("health", 0)
                    item.mana = item_data.get("mana", 0)
                    item.physical_protection = item_data.get("physical_protection", 0)
                    item.magical_protection = item_data.get("magical_protection", 0)
                    item.cooldown_reduction = item_data.get("cooldown_reduction", 0)
                    item.critical_chance = item_data.get("critical_chance", 0)
                    item.lifesteal = item_data.get("lifesteal", 0)
                    
                    db.session.add(item)
                    logger.info(f"✅ ADDED ESSENTIAL ITEM: {item.name}")
            
            db.session.commit()
            logger.info(f"✅ NUCLEAR CLEANUP COMPLETED")
    
    def validate_cleanup(self):
        """Validate the cleanup results."""
        logger.info("✅ Validating cleanup results...")
        
        with app.app_context():
            gods_count = db.session.query(God).count()
            items_count = db.session.query(Item).count()
            
            # Check for any remaining contamination
            contaminated_items = db.session.query(Item).filter(Item.name.in_(SMITE2_GODS)).count()
            invalid_items = db.session.query(Item).filter(~Item.name.in_(SMITE2_ITEMS)).count()
            
            # List all gods and items for verification
            all_gods = db.session.query(God).all()
            all_items = db.session.query(Item).all()
            
            logger.info(f"📊 CLEANUP RESULTS:")
            logger.info(f"   Total gods: {gods_count}")
            logger.info(f"   Total items: {items_count}")
            logger.info(f"   Contaminated items remaining: {contaminated_items}")
            logger.info(f"   Invalid items remaining: {invalid_items}")
            logger.info(f"   Gods moved: {self.gods_moved}")
            logger.info(f"   Items removed: {self.contaminated_removed}")
            logger.info(f"   Duplicates removed: {self.duplicates_removed}")
            
            logger.info("🔍 CURRENT GODS:")
            for god in all_gods:
                logger.info(f"   - {god.name} ({god.role})")
            
            logger.info("🔍 CURRENT ITEMS:")
            for item in all_items:
                logger.info(f"   - {item.name} ({item.cost}g)")
            
            if contaminated_items == 0 and invalid_items == 0:
                logger.info("🎉 EMERGENCY CLEANUP SUCCESSFUL!")
                return True
            else:
                logger.error(f"❌ Emergency cleanup failed - {contaminated_items} contaminated items, {invalid_items} invalid items")
                return False

def main():
    """Main emergency cleanup function."""
    print("🚨 SMITE 2 DIVINE ARSENAL - EMERGENCY DATA CLEANUP")
    print("=" * 60)
    print(f"Database: {db_config.get_database_type()}")
    print(f"URI: {db_config.get_database_uri()}")
    print()
    
    # Initialize cleaner
    cleaner = EmergencyDataCleaner()
    
    try:
        with app.app_context():
            # Perform nuclear cleanup
            cleaner.nuclear_cleanup()
            
            # Validate results
            success = cleaner.validate_cleanup()
            
            if success:
                print("🎉 EMERGENCY DATA CLEANUP COMPLETED SUCCESSFULLY!")
                print(f"✅ Database is now clean and ready for build optimizer testing")
            else:
                print("❌ EMERGENCY DATA CLEANUP FAILED - Check logs for details")
                
    except Exception as e:
        logger.error(f"❌ Error during emergency cleanup: {e}")
        print(f"❌ Emergency cleanup failed: {e}")

if __name__ == "__main__":
    main() 