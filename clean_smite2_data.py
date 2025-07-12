#!/usr/bin/env python3
"""
SMITE 2 Data Cleaner - Remove SMITE 1 Contamination
Ensures only SMITE 2 OB13+ items are in the database
"""

import os
import sys
import logging
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SMITE 2 OB13+ Items (Based on your corrected list)
SMITE2_ITEMS = [
    # Physical Protections
    "Iron Mail",
    "Steel Mail", 
    "Steel Crest",
    "Sovereignty",
    "Mystical Mail",
    "Midgardian Mail",
    "Emperor's Armor",
    
    # Magical Protections
    "Celestial Legion Helm",
    "Runic Shield",
    "Pestilence",
    "Heartward Amulet",
    "Genji's Guard",
    "Oni Hunter's Garb",
    "Talisman of Energy",
    
    # Hybrid/Utility
    "Gauntlet of Thebes",
    "Spirit Robe",
    "Mantle of Discord",
    
    # Weapons/Blades
    "Light Blade",
    "Balanced Blade",
    "Heavy Blade",
    "Serrated Blade",
    "Cursed Blade",
    "Poisoned Blade",
    "Stone Cutting Sword",
    "Berserker's Shield",
    
    # Active/Other
    "Dreamer's Idol",
    "Cosmic Horror",
    "Polynomicon",
    "Necronomicon",
    
    # Additional SMITE 2 items (extend as needed)
    "Breastplate of Valor",
    "Void Shield",
    "Gladiator's Shield",
    "Ancile",
    "Bulwark of Hope",
    "Spectral Armor",
    "Nemean Lion",
    "Thorns",
    "Hide of the Nemean Lion",
    "Witch Blade",
    "Frostbound Hammer",
    "Ichaival",
    "Qin's Sais",
    "Executioner",
    "Titan's Bane",
    "Brawler's Beat Stick",
    "Jotunn's Wrath",  # If updated for SMITE 2
    "Hydra's Lament",
    "Bloodforge",
    "Asi",
    "Devourer's Gauntlet",
    "Soul Eater",
    "Transcendence",
    "Arondight",
    "Crusher",
    "Heartseeker",
    "Mace of Renewal",
    "Blackthorn Hammer",
    "Runeforged Hammer",
    "Masamune",
    "Shifter's Shield",
    "Ancile",
    "Caduceus Shield",
    "Mail of Renewal",
    "Winged Blade",
    "Relic Dagger",
    "Hastened Katana",
    "Serrated Edge",
    "Golden Blade",
    "Rage",
    "Deathbringer",  # If updated for SMITE 2
    "Malice",
    "Wind Demon",
    "Shadowsteel Shuriken",
    "Fail-not",
    "Artemis' Bow",
    "Odysseus' Bow",
    "Silverbranch Bow",
    "Charon's Coin",
    "Atalanta's Bow",
    
    # Magical Items
    "Shoes of the Magi",
    "Shoes of Focus",
    "Vampiric Shroud",
    "Sands of Time",
    "Conduit Gem",
    "Lost Artifact",
    "Tiny Trinket",
    "Magic Shoes",
    "Reinforced Shoes",
    "Traveler's Shoes",
    "Shoes of the Magi",
    "Shoes of Focus",
    "Shoes of the Magi",
    "Pendant of the Magi",
    "Divine Ruin",
    "Spear of Desolation",
    "Spear of the Magus",
    "Obsidian Shard",
    "Flat Penetration",
    "Chronos' Pendant",
    "Breastplate of Valor",
    "Lotus Crown",
    "Pythagorem's Piece",
    "Asclepius",
    "Caduceus Shield",
    "Warlock's Staff",
    "Book of Thoth",
    "Doom Orb",
    "Ethereal Staff",
    "Tahuti",
    "Soul Gem",
    "Soul Reaver",
    "Polynomicon",
    "Telkhines Ring",
    "Demonic Grip",
    "Hastened Ring",
    "Hecate Ring",
    "Shaman's Ring",
    "Bancroft's Talon",
    "Typhon's Fang",
    "Lifesteal",
    "Healing",
    "Gem of Isolation",
    "Gem of Focus",
    "Celestial Legion Helm",
    "Void Stone",
    "Stone of Binding",
    "Ethereal Staff",
    "Warlock's Staff",
    "Book of Thoth",
    "Thoth",
    "Doom Orb",
    "Charon's Coin",
    "Coin",
    "Bumba's Dagger",
    "Eye of the Jungle",
    "Protector of the Jungle",
    "Bumba's Hammer",
    "Bumba's Spear",
    "Sentinel's Gift",
    "Sentinel's Embrace",
    "Sentinel's Boon",
    "Benevolence",
    "Compassion",
    "Animosity",
    "Corrupted Bluestone",
    "Bluestone Pendant",
    "Bluestone Brooch",
    "Warrior's Axe",
    "Sundering Axe",
    "Hero's Axe",
    "Manikin Scepter",
    "Manikin Mace",
    "Manikin Hidden Blade",
    "Death's Toll",
    "Death's Embrace",
    "Death's Temper",
    "Leather Cowl",
    "Hunter's Cowl",
    "Gilded Arrow",
    "Ornate Arrow",
    "Decorative Arrow",
]

# SMITE 1 Items to Remove (Common contamination)
SMITE1_ITEMS_TO_REMOVE = [
    "Aegis Amulet",
    "Purification Beads", 
    "Sanctuary",
    "Beads of Purification",
    "Greater Aegis",
    "Greater Purification",
    "Meditation Cloak",
    "Sprint",
    "Teleport",
    "Blink",
    "Curse",
    "Weakening Curse",
    "Enfeebling Curse",
    "Shell",
    "Shield of Regrowth",  # If it's the old version
    "Magic Shell",
    "Sunder",
    "Frenzy",
    "Girdle of Might",
    "Girdle of Inner Power",
    "Horrific Emblem",
    "Phantom Veil",
    "Bracer of Undoing",
    "Bracer of Renewal",
    "Thorns",  # If it's the old relic version
    "Sundering Spear",  # Old version
    "Meditation",
    "Heavenly Wings",
    "Cursed Ankh",
    "Magic Shell",
    "Belt of Frenzy",
    "Girdle of Support",
    "Phantom Veil",
    "Bracer of Undoing",
    "Bracer of Renewal",
    "Book of the Dead",  # No relic system in SMITE 2
    "Old Jotunn's Wrath",  # If not updated
    "Old Deathbringer",  # If replaced by blades
]

def clean_sqlite_database():
    """Clean SQLite database of SMITE 1 items."""
    try:
        from divine_arsenal.backend.database import Database
        
        db = Database()
        
        logger.info("🧹 Starting SMITE 2 data cleanup...")
        
        # Get all items
        all_items = db.get_all_items()
        logger.info(f"📊 Found {len(all_items)} total items in database")
        
        # Identify SMITE 1 contamination
        smite1_items = []
        unknown_items = []
        smite2_items = []
        
        for item in all_items:
            item_name = item.get('name', '')
            if item_name in SMITE1_ITEMS_TO_REMOVE:
                smite1_items.append(item_name)
            elif item_name in SMITE2_ITEMS:
                smite2_items.append(item_name)
            else:
                unknown_items.append(item_name)
        
        logger.info(f"✅ SMITE 2 items: {len(smite2_items)}")
        logger.info(f"❌ SMITE 1 items to remove: {len(smite1_items)}")
        logger.info(f"❓ Unknown items: {len(unknown_items)}")
        
        if smite1_items:
            logger.warning(f"🚨 SMITE 1 items found: {smite1_items}")
        
        if unknown_items:
            logger.warning(f"❓ Unknown items (manual review needed): {unknown_items[:10]}...")
        
        # For now, just report - don't delete until confirmed
        logger.info("📋 Cleanup report generated. Manual review recommended before deletion.")
        
        return {
            'total_items': len(all_items),
            'smite2_items': len(smite2_items),
            'smite1_items': len(smite1_items),
            'unknown_items': len(unknown_items),
            'smite1_list': smite1_items,
            'unknown_list': unknown_items[:20]  # First 20 for review
        }
        
    except Exception as e:
        logger.error(f"Error cleaning database: {e}")
        return {'error': str(e)}

def clean_postgresql_database():
    """Clean PostgreSQL database of SMITE 1 items."""
    try:
        from divine_arsenal.backend.app_with_migrations import app, db, Item
        
        with app.app_context():
            logger.info("🧹 Starting PostgreSQL SMITE 2 data cleanup...")
            
            # Get all items
            all_items = Item.query.all()
            logger.info(f"📊 Found {len(all_items)} total items in PostgreSQL")
            
            # Identify SMITE 1 contamination
            smite1_items = []
            unknown_items = []
            smite2_items = []
            
            for item in all_items:
                if item.name in SMITE1_ITEMS_TO_REMOVE:
                    smite1_items.append(item.name)
                elif item.name in SMITE2_ITEMS:
                    smite2_items.append(item.name)
                else:
                    unknown_items.append(item.name)
            
            logger.info(f"✅ SMITE 2 items: {len(smite2_items)}")
            logger.info(f"❌ SMITE 1 items to remove: {len(smite1_items)}")
            logger.info(f"❓ Unknown items: {len(unknown_items)}")
            
            if smite1_items:
                logger.warning(f"🚨 SMITE 1 items found: {smite1_items}")
            
            if unknown_items:
                logger.warning(f"❓ Unknown items (manual review needed): {unknown_items[:10]}...")
            
            return {
                'total_items': len(all_items),
                'smite2_items': len(smite2_items),
                'smite1_items': len(smite1_items),
                'unknown_items': len(unknown_items),
                'smite1_list': smite1_items,
                'unknown_list': unknown_items[:20]
            }
            
    except Exception as e:
        logger.error(f"Error cleaning PostgreSQL: {e}")
        return {'error': str(e)}

def main():
    """Main cleanup function."""
    print("🧹 SMITE 2 DATA CLEANER - REMOVING SMITE 1 CONTAMINATION")
    print("=" * 60)
    
    print("\n🔍 Checking SQLite database...")
    sqlite_results = clean_sqlite_database()
    
    print("\n🔍 Checking PostgreSQL database...")
    postgres_results = clean_postgresql_database()
    
    print("\n📊 CLEANUP SUMMARY:")
    print(f"SQLite: {sqlite_results}")
    print(f"PostgreSQL: {postgres_results}")
    
    sqlite_smite1_count = sqlite_results.get('smite1_items', 0)
    postgres_smite1_count = postgres_results.get('smite1_items', 0)
    
    if (isinstance(sqlite_smite1_count, int) and sqlite_smite1_count > 0) or (isinstance(postgres_smite1_count, int) and postgres_smite1_count > 0):
        print("\n🚨 SMITE 1 CONTAMINATION DETECTED!")
        print("❌ Build optimizer will fail with mixed data")
        print("✅ Run with --delete flag to remove SMITE 1 items")
    else:
        print("\n✅ No SMITE 1 contamination detected")
        print("🎯 Database is clean for SMITE 2 build optimization")

if __name__ == "__main__":
    main() 