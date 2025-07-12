#!/usr/bin/env python3
"""Quick check of patches in database"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "divine_arsenal", "backend"))

try:
    from database import Database
except ImportError as e:
    print(f"❌ Database module not found: {e}")
    print("   Make sure you're in the correct directory")
    exit(1)

def main():
    db = Database()
    patches = db.get_patches()
    
    print(f"📊 Total patches in database: {len(patches)}")
    print("\n🎮 Patches:")
    for patch in patches:
        print(f"   {patch.get('version', 'Unknown')}: {patch.get('title', 'Unknown')} ({patch.get('date', 'Unknown')})")

if __name__ == "__main__":
    main() 