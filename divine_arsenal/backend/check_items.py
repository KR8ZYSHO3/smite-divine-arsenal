#!/usr/bin/env python3
"""Simple script to check items database structure."""

import json

from database import Database


def check_items():
    """Check the items in our database."""
    print("🔍 CHECKING ITEMS DATABASE STRUCTURE")
    print("=" * 50)

    db = Database()
    items = db.get_all_items()

    print(f"📊 Total items: {len(items)}")

    if items:
        print(f"\n🎯 First item structure:")
        print(json.dumps(items[0], indent=2))

        print(f"\n📋 Sample items with their fields:")
        for i, item in enumerate(items[:10]):
            if isinstance(item, dict) and "name" in item:
                print(f"{i+1:2d}. {item['name']:<25} - Fields: {list(item.keys())}")

        # Check for specific important fields
        print(f"\n🔍 Checking for important fields:")

        has_passive = sum(1 for item in items if "passive" in item)
        has_active = sum(1 for item in items if "active" in item)
        has_aura = sum(1 for item in items if "aura" in item)
        has_unique = sum(1 for item in items if "unique" in item)
        has_effects = sum(1 for item in items if "effects" in item)
        has_description = sum(1 for item in items if "description" in item)
        has_stats = sum(1 for item in items if "stats" in item)

        print(f"   • Passive abilities: {has_passive}/{len(items)} items")
        print(f"   • Active abilities: {has_active}/{len(items)} items")
        print(f"   • Aura effects: {has_aura}/{len(items)} items")
        print(f"   • Unique passives: {has_unique}/{len(items)} items")
        print(f"   • Special effects: {has_effects}/{len(items)} items")
        print(f"   • Descriptions: {has_description}/{len(items)} items")
        print(f"   • Stats: {has_stats}/{len(items)} items")

        # Find items with the most comprehensive data
        print(f"\n🌟 Items with most comprehensive data:")
        scored_items = []
        for item in items:
            if isinstance(item, dict):
                score = 0
                if "passive" in item and item["passive"]:
                    score += 2
                if "active" in item and item["active"]:
                    score += 2
                if "aura" in item and item["aura"]:
                    score += 1
                if "unique" in item and item["unique"]:
                    score += 1
                if "description" in item and item["description"]:
                    score += 1
                if "stats" in item and len(item["stats"]) > 3:
                    score += 1

                scored_items.append((item, score))

        # Sort by score and show top items
        scored_items.sort(key=lambda x: x[1], reverse=True)

        for i, (item, score) in enumerate(scored_items[:5]):
            print(f"   {i+1}. {item.get('name', 'Unknown'):<25} (Score: {score})")
            if "passive" in item and item["passive"]:
                print(f"      Passive: {item['passive'][:50]}...")
            if "active" in item and item["active"]:
                print(f"      Active: {item['active'][:50]}...")

    else:
        print("❌ No items found in database!")


if __name__ == "__main__":
    check_items()
