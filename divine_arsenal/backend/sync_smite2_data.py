#!/usr/bin/env python3
"""Sync real Smite 2 data from wiki to database."""

import json
from datetime import datetime

from scrapers.wiki_smite2 import WikiSmite2Scraper

from divine_arsenal.backend.database import Database


def serialize_for_db(record):
    """Convert dict/list fields to JSON strings for database storage."""
    for key, value in record.items():
        if isinstance(value, (dict, list)):
            record[key] = json.dumps(value)
    return record


def validate_smite2_god_data(god_data):
    """Validate and clean scraped Smite 2 god data."""
    if "name" not in god_data or not god_data["name"]:
        return False, "Missing or empty name"

    # Ensure required fields exist
    required_fields = ["role", "stats", "scaling_info"]
    for field in required_fields:
        if field not in god_data:
            god_data[field] = {} if field == "stats" else ""

    # Ensure stats is a dict
    if not isinstance(god_data.get("stats"), dict):
        god_data["stats"] = {}

    # Ensure scaling_info is a dict
    if not isinstance(god_data.get("scaling_info"), dict):
        god_data["scaling_info"] = {}

    # Ensure other optional fields exist
    optional_fields = [
        "damage_type",
        "image_url",
        "counter_gods",
        "counter_items",
        "synergy_items",
        "meta_role",
    ]
    for field in optional_fields:
        if field not in god_data:
            if field in ["counter_gods", "counter_items", "synergy_items"]:
                god_data[field] = []
            else:
                god_data[field] = ""

    return True, "Valid"


def validate_smite2_item_data(item_data):
    """Validate and clean scraped Smite 2 item data."""
    if "name" not in item_data or not item_data["name"]:
        return False, "Missing or empty name"

    # Ensure required fields exist
    required_fields = ["cost", "tier", "category", "stats", "tags"]
    for field in required_fields:
        if field not in item_data:
            if field == "stats":
                item_data[field] = {}
            elif field == "tags":
                item_data[field] = []
            elif field == "cost":
                item_data[field] = 0
            elif field == "tier":
                item_data[field] = 0
            else:
                item_data[field] = ""

    # Ensure stats is a dict
    if not isinstance(item_data.get("stats"), dict):
        item_data["stats"] = {}

    # Ensure tags is a list
    if not isinstance(item_data.get("tags"), list):
        item_data["tags"] = []

    # Ensure tier is int
    try:
        item_data["tier"] = int(item_data["tier"])
    except (ValueError, TypeError):
        item_data["tier"] = 0

    # Ensure cost is int
    try:
        item_data["cost"] = int(item_data["cost"])
    except (ValueError, TypeError):
        item_data["cost"] = 0

    # Ensure passive field exists
    if "passive" not in item_data:
        item_data["passive"] = ""

    return True, "Valid"


def main():
    """Sync Smite 2 data from wiki to database."""
    print("🗡️ Syncing Real Smite 2 Data from Wiki...")

    # Initialize components
    db = Database()
    scraper = WikiSmite2Scraper()

    print("🧹 Clearing old data...")
    # Clear existing data
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM god_abilities")
        cursor.execute("DELETE FROM god_relationships")
        cursor.execute("DELETE FROM god_playstyles")
        cursor.execute("DELETE FROM gods")
        cursor.execute("DELETE FROM item_tags")
        cursor.execute("DELETE FROM item_stats")
        cursor.execute("DELETE FROM items")
        cursor.execute("DELETE FROM patches")
        conn.commit()

    # Sync gods
    print("👥 Fetching gods from Smite 2 Wiki...")
    gods = scraper.get_all_gods()
    print(f"✅ Found {len(gods)} gods")

    successful_gods = 0
    for i, god in enumerate(gods, 1):
        try:
            # Validate and clean god data
            is_valid, message = validate_smite2_god_data(god)
            if not is_valid:
                print(f"⚠️ Skipping god {i}: {message}")
                continue

            db.add_god(serialize_for_db(god))
            print(f"  ✅ {god['name']}")
            successful_gods += 1
        except Exception as e:
            print(f"  ❌ Failed to add {god.get('name', f'God {i}')}: {e}")

    # Sync items
    print("\n⚔️ Fetching items from Smite 2 Wiki...")
    items = scraper.get_all_items()
    print(f"✅ Found {len(items)} items")

    successful_items = 0
    for i, item in enumerate(items, 1):
        try:
            # Validate and clean item data
            is_valid, message = validate_smite2_item_data(item)
            if not is_valid:
                print(f"⚠️ Skipping item {i}: {message}")
                continue

            db.add_item(serialize_for_db(item))
            print(f"  ✅ {item['name']}")
            successful_items += 1
        except Exception as e:
            print(f"  ❌ Failed to add {item.get('name', f'Item {i}')}: {e}")

    # Sync patches
    print("\n📝 Fetching patch notes from Smite 2 Wiki...")
    patches = scraper.get_patch_notes()
    print(f"✅ Found {len(patches)} patches")

    successful_patches = 0
    for patch in patches:
        try:
            db.add_patch(
                version=patch.get("version", "Unknown"),
                date=patch.get("date", datetime.now().strftime("%Y-%m-%d")),
                notes=patch.get("content", ""),
                title=patch.get("title", ""),
                url=patch.get("url", ""),
                source="wiki",
            )
            print(f"  ✅ {patch.get('title', 'Unknown')}")
            successful_patches += 1
        except Exception as e:
            print(f"  ❌ Failed to add {patch.get('title', 'Unknown')}: {e}")

    # Final verification
    gods_count = len(db.get_all_gods())
    items_count = len(db.get_all_items())

    print(f"\n📊 Smite 2 Sync Summary:")
    print(f"  Gods imported: {successful_gods}/{len(gods)}")
    print(f"  Items imported: {successful_items}/{len(items)}")
    print(f"  Patches imported: {successful_patches}/{len(patches)}")
    print(f"  Total gods in DB: {gods_count}")
    print(f"  Total items in DB: {items_count}")

    print("✅ Smite 2 data sync complete!")


if __name__ == "__main__":
    main()
