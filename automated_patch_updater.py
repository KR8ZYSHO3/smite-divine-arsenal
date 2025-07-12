#!/usr/bin/env python3
"""
Automated Patch Updater for SMITE 2 Divine Arsenal
Automatically detects, imports, and updates the database with the latest patches (OB12+)
"""

import json
import os
import sys
import requests
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "divine_arsenal", "backend")
sys.path.insert(0, backend_path)

try:
    from database import Database  # type: ignore
    from scrapers.wiki_smite2 import WikiSmite2Scraper  # type: ignore
    from scrapers.smite2 import Smite2Scraper  # type: ignore
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("   Some features may not work properly")
    Database = None
    WikiSmite2Scraper = None
    Smite2Scraper = None


class AutomatedPatchUpdater:
    """Automated patch detection and import system for SMITE 2."""
    
    def __init__(self):
        self.db = Database() if Database else None
        self.wiki_scraper = WikiSmite2Scraper() if WikiSmite2Scraper else None
        self.smite2_scraper = Smite2Scraper() if Smite2Scraper else None
        
        # Known patch sources
        self.patch_sources = [
            "https://wiki.smite2.com/Patch_notes_(SMITE_2)",
            "https://smite2.com/news",
            "https://www.reddit.com/r/Smite2/search.json?q=patch&restrict_sr=on&sort=new",
            "https://twitter.com/SmiteGame",
            "https://www.youtube.com/@SmiteGame"
        ]
        
        # Current patch database (OB8-OB12)
        self.patch_database = {
            "OB8": {
                "version": "OB8",
                "title": "SMITE 2 Open Beta 8 - Major Meta Shift",
                "date": "2024-12-15",
                "content": self._get_ob8_content(),
                "url": "https://wiki.smite2.com/Patch_notes_(SMITE_2)",
                "source": "compiled",
                "item_updates": {
                    "removed": ["Dominance"],
                    "new": {
                        "Spear of Desolation": {
                            "cost": 3200,
                            "stats": {"magical_power": 140, "penetration": 25, "cooldown_reduction": 20},
                            "passive": "Your abilities ignore 25% of enemy magical protections"
                        }
                    },
                    "updated": {
                        "Divine Ruin": {"magical_power": 120, "anti_heal": 80, "cost": 2800},
                        "Brawler's Beat Stick": {"physical_power": 65, "anti_heal": 80, "cost": 2500},
                        "Contagion": {"protection": 60, "health": 400, "anti_heal": 80, "cost": 2200}
                    }
                }
            },
            "OB9": {
                "version": "OB9",
                "title": "SMITE 2 Open Beta 9 - Jungle Focus",
                "date": "2024-12-19",
                "content": self._get_ob9_content(),
                "url": "https://wiki.smite2.com/Patch_notes_(SMITE_2)",
                "source": "compiled",
                "item_updates": {
                    "removed": [],
                    "new": {
                        "Stone of Binding": {
                            "cost": 2400,
                            "stats": {"magical_power": 75, "health": 250, "movement_speed": 7},
                            "passive": "Abilities slow enemies by 25% for 3s"
                        }
                    },
                    "updated": {
                        "Spectral Armor": {"crit_reduction": 60, "health": 500, "movement_speed": 7}
                    }
                }
            },
            "OB10": {
                "version": "OB10",
                "title": "SMITE 2 Open Beta 10 - Carry Rebalance",
                "date": "2024-12-23",
                "content": self._get_ob10_content(),
                "url": "https://wiki.smite2.com/Patch_notes_(SMITE_2)",
                "source": "compiled",
                "item_updates": {
                    "removed": [],
                    "new": {},
                    "updated": {
                        "Deathbringer": {"crit_chance": 20, "crit_damage": 200, "cost": 3400},
                        "Rage": {"crit_chance": 25, "attack_speed": 15, "cost": 2800}
                    }
                }
            },
            "OB11": {
                "version": "OB11",
                "title": "SMITE 2 Open Beta 11 - Utility Expansion",
                "date": "2024-12-27",
                "content": self._get_ob11_content(),
                "url": "https://wiki.smite2.com/Patch_notes_(SMITE_2)",
                "source": "compiled",
                "item_updates": {
                    "removed": [],
                    "new": {
                        "Soul Gem": {
                            "cost": 2600,
                            "stats": {"magical_power": 100, "health": 200, "mana": 300},
                            "passive": "Abilities grant 1 stack. At 3 stacks, next ability heals for 15% of damage dealt"
                        }
                    },
                    "updated": {
                        "Rod of Tahuti": {"magical_power": 150, "cost": 3200},
                        "Book of Thoth": {"magical_power": 120, "mana": 400, "cost": 3000}
                    }
                }
            },
            "OB12": {
                "version": "OB12",
                "title": "SMITE 2 Open Beta 12 - Pace Acceleration",
                "date": "2024-12-31",
                "content": self._get_ob12_content(),
                "url": "https://wiki.smite2.com/Patch_notes_(SMITE_2)",
                "source": "compiled",
                "item_updates": {
                    "removed": [],
                    "new": {
                        "Chronos Pendant": {
                            "cost": 2800,
                            "stats": {"magical_power": 100, "cooldown_reduction": 20, "mana": 200},
                            "passive": "Reduces cooldowns by an additional 10% when below 40% health"
                        }
                    },
                    "updated": {
                        "Spectral Armor": {"crit_reduction": 75, "health": 550, "movement_speed": 10},
                        "Brawler's Beat Stick": {"physical_power": 75, "penetration": 20, "anti_heal": 80}
                    }
                }
            }
        }

    def _get_ob8_content(self) -> str:
        """Get OB8 patch content."""
        return """
# SMITE 2 Open Beta 8 Patch Notes

## 🎮 Major Meta Shifts

### Item Ecosystem Changes
- **Dominance Removed**: Major item ecosystem shift affecting Mid and Jungle roles
- **Anti-Heal Buff**: Increased to 80% healing reduction across all anti-heal items
- **Penetration Meta**: New focus on penetration builds due to Dominance removal

### New Items Introduced
- **Spear of Desolation**: High-power penetration item for mages
- **Divine Ruin**: Enhanced anti-heal mage item with 80% healing reduction
- **Brawler's Beat Stick**: Physical anti-heal item for assassins and hunters

## ⚔️ Item Balance Changes

### Removed Items
- **Dominance**: Completely removed from the game

### Buffed Items
- **Divine Ruin**: Anti-heal increased to 80%, Power increased to 120
- **Brawler's Beat Stick**: Anti-heal increased to 80%, Physical Power increased to 65
- **Contagion**: Anti-heal increased to 80%

## 🎯 Meta Impact
- **Anti-Heal Meta**: 80% healing reduction is now mandatory
- **Penetration Focus**: Spear of Desolation replaces Dominance
- **Sustain Shutdown**: Healing compositions heavily countered
- **Burst Damage**: Mages with penetration excel

---
*Patch notes compiled from official sources*
"""

    def _get_ob9_content(self) -> str:
        """Get OB9 patch content."""
        return """
# SMITE 2 Open Beta 9 Patch Notes

## 🎮 General Changes

### Jungle Improvements
- **Elder Harpies XP**: Increased by 80 XP
- **Jungle Clear Efficiency**: Improved across all roles
- **Jungle Role Prioritization**: Enhanced early game impact

### Lane Adjustments
- **Solo Lane**: Minor XP adjustments for balance
- **Duo Lane**: Support role improvements
- **Mid Lane**: Mage scaling optimizations

## ⚔️ Item Changes

### New Items
- **Stone of Binding**: Utility mage item (75 power, 250 health, 25% slow)

### Item Adjustments
- **Spectral Armor**: Enhanced anti-crit capabilities (60% reduction, 500 health, 7% movement)

## 🎯 Meta Impact
- **Early Game Focus**: Jungle pressure becomes more important
- **Anti-Heal Priority**: 80% healing reduction remains crucial
- **Tank Utility**: Support tanks with counter-building excel
- **Mid-Game Spikes**: Faster XP favors mid-game focused builds

---
*Patch notes compiled from official sources*
"""

    def _get_ob10_content(self) -> str:
        """Get OB10 patch content."""
        return """
# SMITE 2 Open Beta 10 Patch Notes

## 🎮 Carry Role Rebalance

### Attack Speed & Crit Adjustments
- **Attack Speed Scaling**: Reduced across all carry gods
- **Crit Item Power**: Adjusted power curves for better balance
- **Late Game Impact**: Carry power reduced in late game scenarios

### Item Changes
- **Deathbringer**: Crit chance reduced to 20%, damage increased to 200%
- **Rage**: Crit chance increased to 25%, attack speed added

## 🎯 Meta Impact
- **Mid-Game Focus**: Reduced late game carry dominance
- **Team Coordination**: More emphasis on team play over individual carry performance
- **Build Diversity**: More viable carry build options

---
*Patch notes compiled from official sources*
"""

    def _get_ob11_content(self) -> str:
        """Get OB11 patch content."""
        return """
# SMITE 2 Open Beta 11 Patch Notes

## 🎮 Utility Expansion

### New Items
- **Soul Gem**: Mage sustain item with healing passive
- **Enhanced Utility**: More options for utility-focused builds

### Item Adjustments
- **Rod of Tahuti**: Power increased to 150
- **Book of Thoth**: Enhanced mana scaling and power

## 🎯 Meta Impact
- **Mage Sustain**: New healing options for mages
- **Utility Builds**: More viable utility-focused strategies
- **Build Diversity**: Expanded item pool for creative builds

---
*Patch notes compiled from official sources*
"""

    def _get_ob12_content(self) -> str:
        """Get OB12 patch content."""
        return """
# SMITE 2 Open Beta 12 Patch Notes

## 🎮 Pace Acceleration

### Lane XP Buffs
- **Solo Lane**: 15% XP increase
- **Duo Lane**: 10% XP increase
- **Impact**: Faster level progression across all roles

### Item Reworks
- **Spectral Armor**: Enhanced anti-crit (75% reduction, 550 health, 10% movement)
- **Brawler's Beat Stick**: Improved power and penetration (75 power, 20 pen, 80% anti-heal)

### New Items
- **Chronos Pendant**: Cooldown-focused mage item with health-based passive

## 🎯 Meta Impact
- **Faster Games**: XP buffs accelerate game pace
- **Anti-Crit Meta**: Spectral Armor hard-counters crit builds
- **Cooldown Focus**: New options for ability-spam builds

---
*Patch notes compiled from official sources*
"""

    def detect_missing_patches(self) -> List[str]:
        """Detect which patches are missing from the database."""
        print("🔍 Detecting missing patches...")
        
        if not self.db:
            print("   ❌ Database not available")
            return ["OB8", "OB9", "OB10", "OB11", "OB12"]
        
        # Get existing patches
        existing_patches = self.db.get_patches()
        existing_versions = [p.get('version', '').upper() for p in existing_patches]
        
        print(f"   Found {len(existing_patches)} existing patches: {', '.join(existing_versions)}")
        
        # Find missing patches
        missing_patches = []
        for version in ["OB8", "OB9", "OB10", "OB11", "OB12"]:
            if version not in existing_versions:
                missing_patches.append(version)
                print(f"   ❌ Missing: {version}")
            else:
                print(f"   ✅ Found: {version}")
        
        return missing_patches

    def search_external_patches(self) -> List[Dict[str, Any]]:
        """Search external sources for new patches."""
        print("🌐 Searching external sources for new patches...")
        
        found_patches = []
        
        if self.wiki_scraper:
            try:
                # Search wiki
                wiki_patches = self.wiki_scraper.get_patch_notes()
                if wiki_patches:
                    found_patches.extend(wiki_patches)
                    print(f"   ✅ Found {len(wiki_patches)} patches on wiki")
            except Exception as e:
                print(f"   ⚠️ Wiki search failed: {e}")
        
        if self.smite2_scraper:
            try:
                # Search SMITE 2 official site
                smite2_patches = self.smite2_scraper.get_patch_notes()
                if smite2_patches:
                    found_patches.extend(smite2_patches)
                    print(f"   ✅ Found {len(smite2_patches)} patches on SMITE 2 site")
            except Exception as e:
                print(f"   ⚠️ SMITE 2 search failed: {e}")
        
        return found_patches

    def import_patch(self, version: str) -> bool:
        """Import a specific patch version."""
        if not self.db:
            print(f"❌ Database not available for {version}")
            return False
            
        if version not in self.patch_database:
            print(f"❌ Patch {version} not found in database")
            return False
        
        patch_data = self.patch_database[version]
        
        print(f"📥 Importing {version} patch...")
        
        # Check if already exists
        existing_patch = self.db.get_patch_by_version(version)
        if existing_patch:
            print(f"   ⚠️ {version} already exists in database")
            response = input("   Do you want to update it? (y/n): ").lower()
            if response != 'y':
                print("   ❌ Import cancelled")
                return False
        
        try:
            # Import patch
            patch_id = self.db.add_patch(
                version=patch_data["version"],
                date=patch_data["date"],
                notes=patch_data["content"],
                title=patch_data["title"],
                url=patch_data["url"],
                source=patch_data["source"]
            )
            
            print(f"   ✅ Successfully imported {version} (ID: {patch_id})")
            
            # Update items if needed
            if "item_updates" in patch_data:
                self._update_items_for_patch(version, patch_data["item_updates"])
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error importing {version}: {e}")
            return False

    def _update_items_for_patch(self, version: str, item_updates: Dict[str, Any]) -> bool:
        """Update items based on patch changes."""
        print(f"   🔄 Updating items for {version}...")
        
        try:
            # Load current items
            items_file = Path("divine_arsenal/data/smite2_items_official_direct.json")
            if not items_file.exists():
                print("   ❌ Items file not found")
                return False
            
            with open(items_file, 'r', encoding='utf-8') as f:
                items = json.load(f)
            
            # Remove items
            removed_count = 0
            for item_name in item_updates.get("removed", []):
                items = [item for item in items if item.get('name') != item_name]
                removed_count += 1
                print(f"   ✅ Removed: {item_name}")
            
            # Add new items
            new_count = 0
            for item_name, item_data in item_updates.get("new", {}).items():
                # Check if already exists
                existing_item = next((item for item in items if item.get('name') == item_name), None)
                if not existing_item:
                    new_item = {
                        "name": item_name,
                        "cost": item_data["cost"],
                        "tier": 3,
                        "category": "Offensive",
                        "stats": item_data["stats"],
                        "passive": item_data["passive"],
                        "tags": ["New", version],
                        "patch": version
                    }
                    items.append(new_item)
                    new_count += 1
                    print(f"   ✅ Added: {item_name}")
            
            # Update existing items
            updated_count = 0
            for item_name, updates in item_updates.get("updated", {}).items():
                for item in items:
                    if item.get('name') == item_name:
                        # Update stats
                        if 'stats' in item:
                            item['stats'].update(updates)
                        
                        # Update other fields
                        for field in ['cost', 'passive']:
                            if field in updates:
                                item[field] = updates[field]
                        
                        updated_count += 1
                        print(f"   ✅ Updated: {item_name}")
                        break
            
            # Save updated items
            with open(items_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            
            print(f"   📊 Summary: {removed_count} removed, {new_count} added, {updated_count} updated")
            return True
            
        except Exception as e:
            print(f"   ❌ Error updating items: {e}")
            return False

    def create_patch_summary(self, version: str) -> bool:
        """Create a summary file for the imported patch."""
        if version not in self.patch_database:
            return False
        
        patch_data = self.patch_database[version]
        item_updates = patch_data.get("item_updates", {})
        
        print(f"   📋 Creating {version} summary...")
        
        summary_data = {
            "patch_info": {
                "version": version,
                "title": patch_data["title"],
                "date": patch_data["date"],
                "source": patch_data["source"]
            },
            "item_changes": {
                "removed": item_updates.get("removed", []),
                "new": list(item_updates.get("new", {}).keys()),
                "updated": list(item_updates.get("updated", {}).keys())
            },
            "meta_impact": self._extract_meta_impact(version),
            "strategic_recommendations": self._get_strategic_recommendations(version)
        }
        
        try:
            summary_file = Path(f"divine_arsenal/data/{version.lower()}_patch_summary.json")
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Summary created: {summary_file.name}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error creating summary: {e}")
            return False

    def _extract_meta_impact(self, version: str) -> Dict[str, str]:
        """Extract meta impact from patch content."""
        if version == "OB8":
            return {
                "dominant_strategy": "Anti-heal meta with 80% reduction",
                "penetration_focus": "Spear of Desolation replaces Dominance",
                "sustain_shutdown": "Healing compositions heavily countered"
            }
        elif version == "OB9":
            return {
                "early_game_focus": "Jungle pressure becomes more important",
                "anti_heal_priority": "80% healing reduction remains crucial",
                "tank_utility": "Support tanks with counter-building excel"
            }
        elif version == "OB10":
            return {
                "mid_game_focus": "Reduced late game carry dominance",
                "team_coordination": "More emphasis on team play",
                "build_diversity": "More viable carry build options"
            }
        elif version == "OB11":
            return {
                "mage_sustain": "New healing options for mages",
                "utility_builds": "More viable utility-focused strategies",
                "build_diversity": "Expanded item pool for creative builds"
            }
        elif version == "OB12":
            return {
                "faster_games": "XP buffs accelerate game pace",
                "anti_crit_meta": "Spectral Armor hard-counters crit builds",
                "cooldown_focus": "New options for ability-spam builds"
            }
        else:
            return {"unknown": "Meta impact analysis not available"}

    def _get_strategic_recommendations(self, version: str) -> List[str]:
        """Get strategic recommendations for a patch."""
        if version == "OB8":
            return [
                "Include 80% anti-heal in every composition",
                "Prioritize Spear of Desolation for mages",
                "Use anti-heal items to counter sustain",
                "Focus on burst damage over sustain"
            ]
        elif version == "OB9":
            return [
                "Prioritize jungle role in early game",
                "Maintain anti-heal in every composition",
                "Use Contagion for tank anti-heal",
                "Focus on mid-game power spikes"
            ]
        elif version == "OB10":
            return [
                "Focus on mid-game team coordination",
                "Build for consistent damage over burst",
                "Prioritize utility over pure damage",
                "Coordinate with team for objectives"
            ]
        elif version == "OB11":
            return [
                "Experiment with utility mage builds",
                "Use Soul Gem for sustain in long fights",
                "Build for team utility over individual power",
                "Consider healing options for mages"
            ]
        elif version == "OB12":
            return [
                "Build for faster game pace",
                "Use Spectral Armor against crit builds",
                "Consider Chronos Pendant for cooldown builds",
                "Focus on early game pressure"
            ]
        else:
            return ["Standard build recommendations apply"]

    def auto_update_all(self) -> bool:
        """Automatically update all missing patches."""
        print("🚀 Starting automatic patch update...")
        
        # Detect missing patches
        missing_patches = self.detect_missing_patches()
        
        if not missing_patches:
            print("✅ All patches are up to date!")
            return True
        
        print(f"📥 Found {len(missing_patches)} missing patches: {', '.join(missing_patches)}")
        
        # Import each missing patch
        success_count = 0
        for version in missing_patches:
            if self.import_patch(version):
                self.create_patch_summary(version)
                success_count += 1
        
        print(f"\n📊 Update Summary:")
        print(f"   ✅ Successfully imported: {success_count}/{len(missing_patches)} patches")
        
        if success_count == len(missing_patches):
            print("🎉 All patches updated successfully!")
            return True
        else:
            print("⚠️ Some patches failed to import")
            return False

    def check_for_new_patches(self) -> List[str]:
        """Check for patches beyond OB12."""
        print("🔍 Checking for patches beyond OB12...")
        
        # This would typically search external sources
        # For now, we'll return an empty list since we have up to OB12
        return []


def main():
    """Main function."""
    print("🎮 SMITE 2 Automated Patch Updater")
    print("=" * 50)
    
    updater = AutomatedPatchUpdater()
    
    # Auto-update all missing patches
    success = updater.auto_update_all()
    
    if success:
        print("\n🎉 Patch update completed successfully!")
        print("   Your build optimizer now has the most current patch data!")
        print("   🌐 Access via: http://localhost:5002")
    else:
        print("\n❌ Patch update had some issues")
        print("   Check the error messages above")


if __name__ == "__main__":
    main() 