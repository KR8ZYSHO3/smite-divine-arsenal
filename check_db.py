#!/usr/bin/env python3
"""Check database contents and test build optimizer"""

import os
import sys

backend_path = os.path.join(os.path.dirname(__file__), "divine_arsenal", "backend")
sys.path.insert(0, backend_path)

from database import Database  # type: ignore
from working_build_optimizer import WorkingBuildOptimizer  # type: ignore


def main():
    print("🔍 CHECKING DATABASE CONTENTS")
    print("=" * 50)

    # Initialize database
    db = Database()
    gods = db.get_all_gods()

    print(f"Total gods in database: {len(gods)}")
    print("\nFirst 15 gods:")
    for i, god in enumerate(gods[:15]):
        print(f"{i+1:2d}. {god.get('name', 'Unknown')} - {god.get('role', 'Unknown')}")

    print("\n" + "=" * 50)
    print("🧪 TESTING BUILD OPTIMIZER")
    print("=" * 50)

    # Test with gods that actually exist
    test_gods = [gods[0], gods[5], gods[10], gods[15]] if len(gods) >= 16 else gods[:4]

    optimizer = WorkingBuildOptimizer(db)

    for god in test_gods:
        god_name = god.get("name", "Unknown")
        role = god.get("role", "Mid")

        print(f"\n🔬 Testing {god_name} {role}:")
        try:
            result = optimizer.optimize_build(god_name, role)
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                items = result.get("items", [])
                print(f"   ✅ Build: {items[:3]}... (total: {len(items)} items)")
                print(f"   💰 Cost: {result.get('total_cost', 0)} gold")
        except Exception as e:
            print(f"   ❌ Exception: {e}")


if __name__ == "__main__":
    main()
