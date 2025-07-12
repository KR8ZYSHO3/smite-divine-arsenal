#!/usr/bin/env python3
"""Initialize database with Smite 2 JSON data."""

import json
import os
import sys

from divine_arsenal.backend.database import Database


def serialize_for_db(record):
    """Convert dict/list fields to JSON strings for database storage."""
    for key, value in record.items():
        if isinstance(value, (dict, list)):
            record[key] = json.dumps(value)
    return record


def load_smite2_json_data():
    """Load Smite 2 data from JSON files."""
    # Get paths relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gods_path = os.path.join(project_root, "data", "gods_with_scaling.json")
    # Use the new direct scrape file
    items_path = os.path.join(project_root, "data", "smite2_items_official_direct.json")

    print(f"Loading Smite 2 data from:")
    print(f"  Gods: {gods_path}")
    print(f"  Items: {items_path}")

    gods_data = []
    items_data = []

    # Load gods
    if os.path.exists(gods_path):
        with open(gods_path, "r", encoding="utf-8") as f:
            gods_data = json.load(f)
        print(f"✅ Loaded {len(gods_data)} Smite 2 gods")
    else:
        print(f"❌ Gods file not found: {gods_path}")

    # Load items
    if os.path.exists(items_path):
        with open(items_path, "r", encoding="utf-8") as f:
            items_data = json.load(f)
        print(f"✅ Loaded {len(items_data)} Smite 2 items")
    else:
        print(f"❌ Items file not found: {items_path}")

    return gods_data, items_data


def validate_smite2_god_data(god_data):
    """Validate and clean Smite 2 god data."""
    if "name" not in god_data:
        return False, "Missing name"

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

    return True, "Valid"


def validate_smite2_item_data(item_data):
    """Validate and clean Smite 2 item data."""
    if "name" not in item_data:
        return False, "Missing name"

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

    return True, "Valid"


def main():
    """Initialize the database with Smite 2 JSON data."""
    print("🗡️ Initializing Divine Arsenal Database with Smite 2 Data...")

    # Initialize database
    db = Database()
    print("✅ Database initialized")

    # Load Smite 2 JSON data
    gods_data, items_data = load_smite2_json_data()

    if not gods_data and not items_data:
        print("❌ No Smite 2 data to import!")
        return

    # Clear existing data first
    print("🧹 Clearing existing data...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gods")
        cursor.execute("DELETE FROM god_abilities")
        cursor.execute("DELETE FROM god_relationships")
        cursor.execute("DELETE FROM god_playstyles")
        cursor.execute("DELETE FROM items")
        cursor.execute("DELETE FROM item_tags")
        cursor.execute("DELETE FROM item_stats")
        conn.commit()

    # Import gods
    print("👥 Importing Smite 2 gods...")
    successful_gods = 0
    for i, god_data in enumerate(gods_data, 1):
        try:
            # Validate and clean god data
            is_valid, message = validate_smite2_god_data(god_data)
            if not is_valid:
                print(f"⚠️ Skipping god {i}: {message}")
                continue

            db.add_god(serialize_for_db(god_data))
            print(f"  ✅ {god_data['name']}")
            successful_gods += 1
        except Exception as e:
            print(f"  ❌ Failed to import god {i}: {e}")

    # Import items
    print("⚔️ Importing Smite 2 items...")
    successful_items = 0
    for i, item_data in enumerate(items_data, 1):
        try:
            # Validate and clean item data
            is_valid, message = validate_smite2_item_data(item_data)
            if not is_valid:
                print(f"⚠️ Skipping item {i}: {message}")
                continue

            db.add_item(serialize_for_db(item_data))
            print(f"  ✅ {item_data['name']}")
            successful_items += 1
        except Exception as e:
            print(f"  ❌ Failed to import item {i}: {e}")

    # Verify import
    gods_count = len(db.get_all_gods())
    items_count = len(db.get_all_items())

    print("\n📊 Smite 2 Import Summary:")
    print(f"  Gods imported: {successful_gods}/{len(gods_data)}")
    print(f"  Items imported: {successful_items}/{len(items_data)}")
    print(f"  Total gods in DB: {gods_count}")
    print(f"  Total items in DB: {items_count}")
    print("✅ Smite 2 database initialization complete!")


if __name__ == "__main__":
    main()
