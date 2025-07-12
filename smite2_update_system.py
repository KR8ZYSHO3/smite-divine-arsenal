#!/usr/bin/env python3
"""
Smite 2 Database Update System
Handles patches, item changes, and database maintenance
"""

import datetime
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


class Smite2UpdateSystem:
    """🔄 SMITE 2 Database Update System with Enhanced Monitoring"""

    def __init__(self, db_path: str = "divine_arsenal/backend/divine_arsenal.db"):
        self.db_path = db_path
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.base_path = Path("divine_arsenal/data")
        self.items_file = self.base_path / "items.json"
        self.backup_dir = self.base_path / "backups"
        self.update_log = self.base_path / "update_log.json"
        self.version_file = self.base_path / "database_version.json"

        # Create directories if they don't exist
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, reason="manual"):
        """Create a timestamped backup of current database."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"items_backup_{timestamp}_{reason}.json"
        backup_path = self.backup_dir / backup_name

        try:
            if self.items_file.exists():
                shutil.copy2(self.items_file, backup_path)
                print(f"✅ Backup created: {backup_name}")
                return backup_path
            else:
                print(f"⚠️  No items file to backup")
                return None
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None

    def get_current_version(self):
        """Get current database version info."""
        try:
            if self.version_file.exists():
                with open(self.version_file, "r") as f:
                    return json.load(f)
            else:
                return {
                    "version": "1.0.0",
                    "last_update": datetime.datetime.now().isoformat(),
                    "patch_version": "Unknown",
                    "item_count": 0,
                }
        except Exception as e:
            print(f"⚠️  Error reading version: {e}")
            return {"version": "1.0.0", "last_update": "Unknown"}

    def update_version(self, new_version, patch_version, item_count):
        """Update version information."""
        version_info = {
            "version": new_version,
            "last_update": datetime.datetime.now().isoformat(),
            "patch_version": patch_version,
            "item_count": item_count,
            "update_history": [],
        }

        # Load existing history
        if self.version_file.exists():
            try:
                with open(self.version_file, "r") as f:
                    old_info = json.load(f)
                    version_info["update_history"] = old_info.get("update_history", [])
            except Exception:
                pass

        # Add current update to history
        version_info["update_history"].append(
            {
                "date": datetime.datetime.now().isoformat(),
                "version": new_version,
                "patch": patch_version,
                "items": item_count,
            }
        )

        # Keep only last 10 updates
        version_info["update_history"] = version_info["update_history"][-10:]

        with open(self.version_file, "w") as f:
            json.dump(version_info, f, indent=2)

    def check_for_updates(self) -> Dict[str, Any]:
        """Check for updates from multiple sources with better error handling."""
        print("🔍 CHECKING FOR SMITE 2 UPDATES")
        print("=" * 50)

        update_sources = {
            "smite2_wiki": "https://wiki.smite2.com/w/Items",
            "smite2_reddit": "https://www.reddit.com/r/Smite2/hot.json",
        }

        results = {}

        for source_name, url in update_sources.items():
            print(f"📡 Checking {source_name.replace('_', ' ').title()}...")
            try:
                # Use session for better connection handling
                session = requests.Session()
                session.headers.update(self.headers)

                response = session.get(url, timeout=15, allow_redirects=True)

                if response.status_code == 200:
                    print(f"   ✅ {source_name.replace('_', ' ').title()} accessible")
                    results[source_name] = {
                        "status": "success",
                        "content_length": len(response.text),
                        "last_modified": response.headers.get("Last-Modified", "Unknown"),
                    }
                elif response.status_code == 403:
                    print(
                        f"   ⚠️  {source_name.replace('_', ' ').title()} returned 403 (Access restricted)"
                    )
                    results[source_name] = {
                        "status": "access_restricted",
                        "message": "Site may be blocking automated requests",
                    }
                elif response.status_code == 429:
                    print(
                        f"   ⚠️  {source_name.replace('_', ' ').title()} returned 429 (Rate limited)"
                    )
                    results[source_name] = {
                        "status": "rate_limited",
                        "message": "Too many requests - try again later",
                    }
                else:
                    print(
                        f"   ⚠️  {source_name.replace('_', ' ').title()} returned {response.status_code}"
                    )
                    results[source_name] = {"status": "error", "status_code": response.status_code}

            except requests.exceptions.Timeout:
                print(f"   ⚠️  {source_name.replace('_', ' ').title()} timed out")
                results[source_name] = {"status": "timeout"}
            except requests.exceptions.ConnectionError:
                print(f"   ⚠️  {source_name.replace('_', ' ').title()} connection failed")
                results[source_name] = {"status": "connection_error"}
            except Exception as e:
                print(f"   ⚠️  {source_name.replace('_', ' ').title()} error: {str(e)}")
                results[source_name] = {"status": "error", "message": str(e)}

        # Analyze results
        accessible_sources = sum(1 for r in results.values() if r.get("status") == "success")

        if accessible_sources == 0:
            print("\n⚠️  All external sources are currently inaccessible")
            print("💡 This is normal - many sites block automated requests")
            print("🛠️  Use manual update options to add new items")
        else:
            print(f"\n✅ {accessible_sources}/{len(update_sources)} sources accessible")

        print("\n✅ Update check complete")

        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "accessible_sources": accessible_sources,
            "total_sources": len(update_sources),
            "results": results,
            "recommendation": (
                "Use manual update for new items"
                if accessible_sources == 0
                else "Some sources available"
            ),
        }

    def manual_update_prompt(self):
        """Interactive prompt for manual database updates."""
        print("\n🛠️  MANUAL UPDATE SYSTEM")
        print("=" * 40)

        current_version = self.get_current_version()
        print(f"📊 Current Version: {current_version.get('version', 'Unknown')}")
        print(f"📅 Last Update: {current_version.get('last_update', 'Unknown')}")
        print(f"🎮 Patch Version: {current_version.get('patch_version', 'Unknown')}")
        print(f"📦 Item Count: {current_version.get('item_count', 0)}")

        print(f"\n🔧 Update Options:")
        print(f"1. Add new items")
        print(f"2. Modify existing items")
        print(f"3. Remove items")
        print(f"4. Full database refresh")
        print(f"5. Import from file")
        print(f"6. Exit")

        return input(f"\nSelect option (1-6): ").strip()

    def add_new_item(self):
        """Interactive item addition."""
        print(f"\n➕ ADD NEW ITEM")
        print(f"=" * 30)

        item = {}
        item["name"] = input("Item name: ").strip()
        item["cost"] = int(input("Cost (gold): ").strip() or "0")
        item["tier"] = int(input("Tier (0-3): ").strip() or "0")
        item["category"] = input("Category (Relic/Offensive/Defensive/Hybrid/Consumable): ").strip()
        item["passive"] = input("Passive description: ").strip()

        # Stats
        print(f"\n📊 Stats (press Enter to skip):")
        stats = {}
        stat_options = [
            "physical_power",
            "magical_power",
            "attack_speed",
            "critical_chance",
            "physical_protection",
            "magical_protection",
            "health",
            "mana",
            "lifesteal",
            "penetration",
            "cooldown_reduction",
        ]

        for stat in stat_options:
            value = input(f"{stat}: ").strip()
            if value:
                try:
                    stats[stat] = int(value)
                except Exception:
                    stats[stat] = float(value)

        item["stats"] = stats

        # Tags
        tags_input = input("Tags (comma-separated): ").strip()
        item["tags"] = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

        return item

    def modify_existing_item(self, items):
        """Interactive item modification."""
        print(f"\n✏️  MODIFY EXISTING ITEM")
        print(f"=" * 35)

        # Show current items
        for i, item in enumerate(items[:10]):
            print(f"{i+1}. {item['name']} - {item['category']}")

        if len(items) > 10:
            print(f"... and {len(items) - 10} more items")

        item_name = input(f"\nEnter item name to modify: ").strip()

        # Find item
        item_to_modify = None
        for item in items:
            if item["name"].lower() == item_name.lower():
                item_to_modify = item
                break

        if not item_to_modify:
            print(f"❌ Item '{item_name}' not found")
            return items

        print(f"\n📋 Current item data:")
        print(json.dumps(item_to_modify, indent=2))

        print(f"\nWhat to modify?")
        print(f"1. Name")
        print(f"2. Cost")
        print(f"3. Stats")
        print(f"4. Passive")
        print(f"5. Category")
        print(f"6. Tags")

        choice = input("Select (1-6): ").strip()

        if choice == "1":
            item_to_modify["name"] = input("New name: ").strip()
        elif choice == "2":
            item_to_modify["cost"] = int(input("New cost: ").strip())
        elif choice == "3":
            print("Enter new stats (format: stat_name=value, e.g., physical_power=50):")
            stats_input = input("Stats: ").strip()
            if stats_input:
                new_stats = {}
                for stat_pair in stats_input.split(","):
                    if "=" in stat_pair:
                        key, value = stat_pair.split("=", 1)
                        try:
                            new_stats[key.strip()] = int(value.strip())
                        except Exception:
                            new_stats[key.strip()] = float(value.strip())
                item_to_modify["stats"] = new_stats
        elif choice == "4":
            item_to_modify["passive"] = input("New passive: ").strip()
        elif choice == "5":
            item_to_modify["category"] = input("New category: ").strip()
        elif choice == "6":
            tags_input = input("New tags (comma-separated): ").strip()
            item_to_modify["tags"] = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

        return items

    def full_database_refresh(self):
        """Refresh entire database with latest items."""
        print(f"\n🔄 FULL DATABASE REFRESH")
        print(f"=" * 35)

        print(f"This will replace your entire items database.")
        print(f"A backup will be created automatically.")

        confirm = input(f"Continue? (y/N): ").strip().lower()
        if confirm != "y":
            print(f"❌ Refresh cancelled")
            return False

        # Create backup
        backup_path = self.create_backup("full_refresh")
        if not backup_path:
            print(f"❌ Could not create backup. Aborting.")
            return False

        # Import fresh data (you would implement this based on your data source)
        print(f"🔄 Refreshing database...")
        print(f"⚠️  This would connect to your preferred data source")
        print(f"📊 For now, keeping existing database structure")

        return True

    def import_from_file(self):
        """Import items from external file."""
        print(f"\n📥 IMPORT FROM FILE")
        print(f"=" * 30)

        file_path = input("Enter file path: ").strip()

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None

        try:
            with open(file_path, "r") as f:
                new_items = json.load(f)

            print(f"✅ Loaded {len(new_items)} items from file")

            # Validate structure
            if isinstance(new_items, list) and len(new_items) > 0:
                sample_item = new_items[0]
                required_fields = ["name", "cost", "category"]

                if all(field in sample_item for field in required_fields):
                    print(f"✅ File structure valid")
                    return new_items
                else:
                    print(f"❌ Invalid item structure. Required fields: {required_fields}")
                    return None
            else:
                print(f"❌ Invalid file format")
                return None

        except Exception as e:
            print(f"❌ Error importing file: {e}")
            return None

    def apply_update(self, new_items, update_type="manual"):
        """Apply update to database."""
        if not new_items:
            print(f"❌ No items to update")
            return False

        # Create backup
        backup_path = self.create_backup(update_type)
        if not backup_path:
            print(f"⚠️  Proceeding without backup")

        # Save new items
        try:
            with open(self.items_file, "w", encoding="utf-8") as f:
                json.dump(new_items, f, indent=2, ensure_ascii=False)

            # Update version
            new_version = f"1.{len(new_items)}.0"
            patch_version = input("Enter patch version (e.g., 2.1.3): ").strip() or "Unknown"

            self.update_version(new_version, patch_version, len(new_items))

            print(f"✅ Database updated successfully!")
            print(f"📊 New item count: {len(new_items)}")
            print(f"🎮 Patch version: {patch_version}")

            return True

        except Exception as e:
            print(f"❌ Error saving update: {e}")
            return False

    def run_update_system(self):
        """Main update system interface."""
        print(f"🔄 SMITE 2 DATABASE UPDATE SYSTEM")
        print(f"=" * 50)

        while True:
            print(f"\n🛠️  UPDATE OPTIONS:")
            print(f"1. Check for updates")
            print(f"2. Manual update")
            print(f"3. View update history")
            print(f"4. Restore from backup")
            print(f"5. Create backup")
            print(f"6. Exit")

            choice = input(f"\nSelect option (1-6): ").strip()

            if choice == "1":
                update_results = self.check_for_updates()
                if update_results.get("accessible_sources", 0) == 0:
                    print(f"\n🔥 Updates may be available!")
                    print(f"💡 Use manual update to add new items")
                else:
                    print(f"\n✅ No obvious updates detected")

            elif choice == "2":
                self.run_manual_update()

            elif choice == "3":
                self.show_update_history()

            elif choice == "4":
                self.restore_from_backup()

            elif choice == "5":
                reason = input("Backup reason: ").strip() or "manual"
                self.create_backup(reason)

            elif choice == "6":
                print(f"👋 Goodbye!")
                break

            else:
                print(f"❌ Invalid choice")

    def run_manual_update(self):
        """Run manual update process."""
        # Load current items
        try:
            with open(self.items_file, "r") as f:
                current_items = json.load(f)
        except Exception:
            current_items = []

        while True:
            choice = self.manual_update_prompt()

            if choice == "1":  # Add new items
                new_item = self.add_new_item()
                if new_item:
                    current_items.append(new_item)
                    print(f"✅ Added item: {new_item['name']}")

            elif choice == "2":  # Modify existing
                current_items = self.modify_existing_item(current_items)

            elif choice == "3":  # Remove items
                item_name = input("Item name to remove: ").strip()
                current_items = [
                    item for item in current_items if item["name"].lower() != item_name.lower()
                ]
                print(f"✅ Removed item: {item_name}")

            elif choice == "4":  # Full refresh
                if self.full_database_refresh():
                    break

            elif choice == "5":  # Import from file
                imported_items = self.import_from_file()
                if imported_items:
                    current_items = imported_items
                    print(f"✅ Imported {len(imported_items)} items")

            elif choice == "6":  # Exit
                break

            # Ask if they want to save changes
            if choice in ["1", "2", "3", "5"]:
                save = input(f"\nSave changes? (y/N): ").strip().lower()
                if save == "y":
                    if self.apply_update(current_items, "manual"):
                        print(f"✅ Changes saved!")
                    else:
                        print(f"❌ Error saving changes")
                    break

    def show_update_history(self):
        """Show database update history."""
        print(f"\n📜 UPDATE HISTORY")
        print(f"=" * 30)

        version_info = self.get_current_version()
        history = version_info.get("update_history", [])

        if not history:
            print(f"No update history available")
            return

        for i, update in enumerate(reversed(history)):
            if isinstance(update, dict):
                print(f"{i+1}. {update.get('date', 'Unknown')}")
                print(f"   Version: {update.get('version', 'Unknown')}")
                print(f"   Patch: {update.get('patch', 'Unknown')}")
                print(f"   Items: {update.get('items', 0)}")
            else:
                print(f"{i+1}. Invalid update entry: {update}")
            print()

    def restore_from_backup(self):
        """Restore database from backup."""
        print(f"\n🔄 RESTORE FROM BACKUP")
        print(f"=" * 35)

        # List available backups
        backups = list(self.backup_dir.glob("*.json"))
        if not backups:
            print(f"❌ No backups found")
            return

        print(f"📋 Available backups:")
        for i, backup in enumerate(backups):
            print(f"{i+1}. {backup.name}")

        try:
            choice = int(input(f"\nSelect backup (1-{len(backups)}): ").strip()) - 1
            selected_backup = backups[choice]

            # Confirm restore
            print(f"\n⚠️  This will replace your current database!")
            confirm = input(f"Restore from {selected_backup.name}? (y/N): ").strip().lower()

            if confirm == "y":
                shutil.copy2(selected_backup, self.items_file)
                print(f"✅ Database restored from {selected_backup.name}")
            else:
                print(f"❌ Restore cancelled")

        except (ValueError, IndexError):
            print(f"❌ Invalid selection")
        except Exception as e:
            print(f"❌ Error restoring backup: {e}")


def main():
    """Main entry point."""
    update_system = Smite2UpdateSystem()
    update_system.run_update_system()


if __name__ == "__main__":
    main()
