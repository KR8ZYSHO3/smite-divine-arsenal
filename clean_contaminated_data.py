#!/usr/bin/env python3
"""
🧹 DATA CLEANUP SCRIPT - SMITE 2 DIVINE ARSENAL
Separates gods from items and cleans contaminated database data
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

class DataCleaner:
    """Handles data cleanup operations."""
    
    def __init__(self):
        self.gods_moved = 0
        self.items_removed = 0
        self.duplicates_removed = 0
        
    def analyze_contamination(self):
        """Analyze the current data contamination."""
        logger.info("🔍 Analyzing data contamination...")
        
        with app.app_context():
            # Check items table for gods
            contaminated_items = db.session.query(Item).filter(Item.name.in_(SMITE2_GODS)).all()
            
            # Check gods table for duplicates
            existing_gods = db.session.query(God).all()
            god_names = [g.name for g in existing_gods]
            
            # Check items table for non-SMITE2 items
            all_items = db.session.query(Item).all()
            invalid_items = [item for item in all_items if item.name not in SMITE2_ITEMS and item.name not in SMITE2_GODS]
            
            logger.info(f"📊 CONTAMINATION ANALYSIS:")
            logger.info(f"   Gods in items table: {len(contaminated_items)}")
            logger.info(f"   Existing gods: {len(existing_gods)}")
            logger.info(f"   Invalid items: {len(invalid_items)}")
            logger.info(f"   Total items: {len(all_items)}")
            
            return {
                'contaminated_items': contaminated_items,
                'existing_gods': existing_gods,
                'invalid_items': invalid_items,
                'total_items': len(all_items)
            }
    
    def clean_gods_from_items(self):
        """Move gods from items table to gods table."""
        logger.info("🔄 Moving gods from items to gods table...")
        
        with app.app_context():
            # Find items that are actually gods
            contaminated_items = db.session.query(Item).filter(Item.name.in_(SMITE2_GODS)).all()
            
            for item in contaminated_items:
                # Check if god already exists
                existing_god = db.session.query(God).filter_by(name=item.name).first()
                
                if not existing_god:
                    # Create new god record
                    god = God()
                    god.name = item.name
                    god.role = "Unknown"  # Will be updated later
                    god.damage_type = "Unknown"
                    god.pantheon = "Unknown"
                    
                    # Transfer any stats from item to god
                    god.health = item.health or 0.0
                    god.mana = item.mana or 0.0
                    god.physical_power = item.physical_power or 0.0
                    god.magical_power = item.magical_power or 0.0
                    god.physical_protection = item.physical_protection or 0.0
                    god.magical_protection = item.magical_protection or 0.0
                    god.attack_speed = item.attack_speed or 0.0
                    god.movement_speed = item.movement_speed or 0.0
                    
                    db.session.add(god)
                    self.gods_moved += 1
                    logger.info(f"✅ Moved {item.name} to gods table")
                else:
                    logger.info(f"⚠️  {item.name} already exists in gods table")
                
                # Remove from items table
                db.session.delete(item)
            
            db.session.commit()
            logger.info(f"✅ Moved {self.gods_moved} gods from items table")
    
    def clean_invalid_items(self):
        """Remove items that are not valid SMITE 2 items."""
        logger.info("🗑️  Removing invalid items...")
        
        with app.app_context():
            # Keep only valid SMITE 2 items
            all_items = db.session.query(Item).all()
            
            for item in all_items:
                if item.name not in SMITE2_ITEMS:
                    db.session.delete(item)
                    self.items_removed += 1
                    logger.info(f"❌ Removed invalid item: {item.name}")
            
            db.session.commit()
            logger.info(f"✅ Removed {self.items_removed} invalid items")
    
    def remove_duplicate_gods(self):
        """Remove duplicate gods."""
        logger.info("🔄 Removing duplicate gods...")
        
        with app.app_context():
            # Find duplicates
            god_names = {}
            all_gods = db.session.query(God).all()
            
            for god in all_gods:
                if god.name in god_names:
                    # This is a duplicate
                    db.session.delete(god)
                    self.duplicates_removed += 1
                    logger.info(f"❌ Removed duplicate god: {god.name}")
                else:
                    god_names[god.name] = god
            
            db.session.commit()
            logger.info(f"✅ Removed {self.duplicates_removed} duplicate gods")
    
    def validate_cleanup(self):
        """Validate the cleanup results."""
        logger.info("✅ Validating cleanup results...")
        
        with app.app_context():
            gods_count = db.session.query(God).count()
            items_count = db.session.query(Item).count()
            
            # Check for any remaining contamination
            contaminated_items = db.session.query(Item).filter(Item.name.in_(SMITE2_GODS)).count()
            
            logger.info(f"📊 CLEANUP RESULTS:")
            logger.info(f"   Total gods: {gods_count}")
            logger.info(f"   Total items: {items_count}")
            logger.info(f"   Contaminated items remaining: {contaminated_items}")
            logger.info(f"   Gods moved: {self.gods_moved}")
            logger.info(f"   Items removed: {self.items_removed}")
            logger.info(f"   Duplicates removed: {self.duplicates_removed}")
            
            if contaminated_items == 0:
                logger.info("🎉 DATA CLEANUP SUCCESSFUL!")
                return True
            else:
                logger.error("❌ Data cleanup failed - contamination still exists")
                return False

def main():
    """Main cleanup function."""
    print("🧹 SMITE 2 DIVINE ARSENAL - DATA CLEANUP")
    print("=" * 60)
    print(f"Database: {db_config.get_database_type()}")
    print(f"URI: {db_config.get_database_uri()}")
    print()
    
    # Initialize cleaner
    cleaner = DataCleaner()
    
    try:
        with app.app_context():
            # Analyze contamination
            analysis = cleaner.analyze_contamination()
            
            if analysis['contaminated_items'] or analysis['invalid_items']:
                # Perform cleanup
                cleaner.clean_gods_from_items()
                cleaner.clean_invalid_items()
                cleaner.remove_duplicate_gods()
                
                # Validate results
                success = cleaner.validate_cleanup()
                
                if success:
                    print("🎉 DATA CLEANUP COMPLETED SUCCESSFULLY!")
                    print(f"✅ Ready for build optimizer testing")
                else:
                    print("❌ DATA CLEANUP FAILED - Check logs for details")
            else:
                print("✅ No data contamination detected - database is clean!")
                
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        print(f"❌ Cleanup failed: {e}")

if __name__ == "__main__":
    main() 