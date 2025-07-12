#!/usr/bin/env python3
"""
SMITE 2 Patch Monitor
Monitors for new patches and alerts when updates are needed.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "divine_arsenal", "backend"))

try:
    from database import Database
except ImportError as e:
    print(f"⚠️ Database module not found: {e}")
    print("   Running in standalone mode.")
    Database = None


class PatchMonitor:
    """Monitor for new SMITE 2 patches."""
    
    def __init__(self):
        self.db = Database() if Database else None
        self.current_patches = ["OB8", "OB9", "OB10", "OB11", "OB12"]
        self.monitor_file = Path("divine_arsenal/data/patch_monitor.json")
        
    def check_current_status(self):
        """Check current patch status."""
        print("🔍 SMITE 2 Patch Monitor")
        print("=" * 40)
        
        if self.db:
            # Check database
            existing_patches = self.db.get_patches()
            existing_versions = [p.get('version', '').upper() for p in existing_patches]
            
            print(f"📋 Database Status:")
            print(f"   Total patches: {len(existing_patches)}")
            print(f"   Versions: {', '.join(existing_versions)}")
            
            # Find missing patches
            missing = [v for v in self.current_patches if v not in existing_versions]
            if missing:
                print(f"   ❌ Missing: {', '.join(missing)}")
            else:
                print("   ✅ All current patches imported")
        else:
            print("📋 Database not available - running in standalone mode")
        
        # Check summary files
        print(f"\n📁 Summary Files:")
        summary_files = [
            "ob8_patch_summary.json",
            "ob9_patch_summary.json", 
            "ob10_patch_summary.json",
            "ob11_patch_summary.json",
            "ob12_patch_summary.json"
        ]
        
        for summary_file in summary_files:
            file_path = Path(f"divine_arsenal/data/{summary_file}")
            if file_path.exists():
                print(f"   ✅ {summary_file}")
            else:
                print(f"   ❌ {summary_file} (Missing)")
        
        # Check items file
        items_file = Path("divine_arsenal/data/smite2_items_official_direct.json")
        if items_file.exists():
            with open(items_file, 'r', encoding='utf-8') as f:
                items = json.load(f)
            print(f"\n⚔️ Items Database:")
            print(f"   Total items: {len(items)}")
            
            # Check for key items
            key_items = {
                "Divine Ruin": "Anti-heal mage item",
                "Brawler's Beat Stick": "Anti-heal physical item", 
                "Contagion": "Anti-heal tank item",
                "Spear of Desolation": "Penetration mage item",
                "Spectral Armor": "Anti-crit tank item",
                "Chronos Pendant": "Cooldown mage item"
            }
            
            print(f"   Key Items Status:")
            for item_name, description in key_items.items():
                item = next((item for item in items if item.get('name') == item_name), None)
                if item:
                    print(f"   ✅ {item_name}: {description}")
                else:
                    print(f"   ❌ {item_name}: {description} (Missing)")
        else:
            print(f"\n❌ Items file not found: {items_file}")
    
    def save_monitor_state(self):
        """Save current monitor state."""
        state = {
            "last_check": datetime.now().isoformat(),
            "current_patches": self.current_patches,
            "status": "monitoring"
        }
        
        try:
            with open(self.monitor_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            print(f"💾 Monitor state saved: {self.monitor_file}")
        except Exception as e:
            print(f"❌ Error saving monitor state: {e}")
    
    def get_recommendations(self):
        """Get recommendations for keeping patches updated."""
        print(f"\n💡 Recommendations:")
        print("-" * 40)
        
        print("1. Run automated updater:")
        print("   python automated_patch_updater.py")
        
        print("\n2. Check for new patches manually:")
        print("   - Visit: https://wiki.smite2.com/Patch_notes_(SMITE_2)")
        print("   - Check: https://smite2.com/news")
        print("   - Monitor: https://reddit.com/r/Smite2")
        
        print("\n3. Update items when new patches drop:")
        print("   - Add new items to smite2_items_official_direct.json")
        print("   - Update existing item stats")
        print("   - Remove deprecated items")
        
        print("\n4. Run status check:")
        print("   python patch_status_report.py")
        
        print("\n5. Test build optimizer:")
        print("   python check_db.py")
    
    def check_for_updates(self):
        """Check if updates are needed."""
        print(f"\n🔄 Update Check:")
        print("-" * 40)
        
        if self.db:
            existing_patches = self.db.get_patches()
            existing_versions = [p.get('version', '').upper() for p in existing_patches]
            missing = [v for v in self.current_patches if v not in existing_versions]
            
            if missing:
                print(f"❌ Updates needed: {', '.join(missing)} patches missing")
                print(f"💡 Run: python automated_patch_updater.py")
                return True
            else:
                print("✅ All patches up to date!")
                return False
        else:
            print("⚠️ Cannot check database - run automated_patch_updater.py to update")
            return True


def main():
    """Main function."""
    monitor = PatchMonitor()
    
    # Check current status
    monitor.check_current_status()
    
    # Check for updates
    needs_update = monitor.check_for_updates()
    
    # Get recommendations
    monitor.get_recommendations()
    
    # Save monitor state
    monitor.save_monitor_state()
    
    if needs_update:
        print(f"\n🚨 ACTION REQUIRED: Run patch updater to get latest patches!")
        return 1
    else:
        print(f"\n✅ All good! Your SMITE 2 Divine Arsenal is up to date.")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 