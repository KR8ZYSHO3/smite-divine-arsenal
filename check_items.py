#!/usr/bin/env python3
"""Simple script to check items database structure."""

import json

from divine_arsenal.backend.database import Database


def check_items():
    """Check the items in our database."""
    print("🔍 CHECKING SMITE 2 ITEMS DATABASE STRUCTURE")
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

        has_passive = sum(1 for item in items if "passive" in item and item["passive"])
        has_stats = sum(1 for item in items if "stats" in item and item["stats"])
        has_tags = sum(1 for item in items if "tags" in item and item["tags"])
        has_category = sum(1 for item in items if "category" in item and item["category"])
        has_tier = sum(1 for item in items if "tier" in item)
        has_cost = sum(1 for item in items if "cost" in item)

        print(f"   • Passive abilities: {has_passive}/{len(items)} items")
        print(f"   • Stats objects: {has_stats}/{len(items)} items")
        print(f"   • Tags: {has_tags}/{len(items)} items")
        print(f"   • Categories: {has_category}/{len(items)} items")
        print(f"   • Tiers: {has_tier}/{len(items)} items")
        print(f"   • Costs: {has_cost}/{len(items)} items")

        # Find items with the most comprehensive data
        print(f"\n🌟 Items with most comprehensive data:")
        scored_items = []
        for item in items:
            if isinstance(item, dict):
                score = 0
                if "passive" in item and item["passive"]:
                    score += 2
                if "stats" in item and item["stats"] and len(item["stats"]) > 0:
                    score += 2
                if "tags" in item and item["tags"] and len(item["tags"]) > 0:
                    score += 1
                if "category" in item and item["category"]:
                    score += 1
                if "tier" in item:
                    score += 1
                if "cost" in item:
                    score += 1

                scored_items.append((item, score))

        # Sort by score and show top items
        scored_items.sort(key=lambda x: x[1], reverse=True)

        for i, (item, score) in enumerate(scored_items[:5]):
            print(f"   {i+1}. {item.get('name', 'Unknown'):<25} (Score: {score})")
            if "passive" in item and item["passive"]:
                print(f"      Passive: {item['passive'][:50]}...")
            if "stats" in item and item["stats"]:
                stats_str = ", ".join([f"{k}: {v}" for k, v in list(item["stats"].items())[:3]])
                print(f"      Stats: {stats_str}")
            if "tags" in item and item["tags"]:
                tags_str = ", ".join(item["tags"][:3])
                print(f"      Tags: {tags_str}")

        # Check tier distribution
        print(f"\n📊 Tier distribution:")
        tier_counts = {}
        for item in items:
            tier = item.get("tier", "Unknown")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        for tier, count in sorted(tier_counts.items()):
            print(f"   • Tier {tier}: {count} items")

        # Check category distribution
        print(f"\n📊 Category distribution:")
        category_counts = {}
        for item in items:
            category = item.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1

        for category, count in sorted(category_counts.items()):
            print(f"   • {category}: {count} items")

    else:
        print("❌ No items found in database!")


if __name__ == "__main__":
    check_items()
