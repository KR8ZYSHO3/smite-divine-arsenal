#!/usr/bin/env python3
"""
Divine Arsenal Launcher
Simple launcher that runs the advanced divine_arsenal system
"""

import os
import subprocess
import sys
from pathlib import Path


print(f"[DEBUG] App startup CWD: {os.getcwd()}")
# If possible, also print the expected DB path
try:
    from divine_arsenal.backend.user_auth import UserAuth
    print(f"[DEBUG] UserAuth default DB path: {os.path.abspath('divine_arsenal/backend/divine_arsenal.db')}")
except Exception as e:
    print(f"[DEBUG] Could not import UserAuth for DB path: {e}")


def main():
    """Launch the Divine Arsenal system."""

    print("🚀 DIVINE ARSENAL - SMITE 2 COMPANION")
    print("=" * 50)

    # Check if divine_arsenal directory exists
    divine_arsenal_dir = Path(__file__).parent / "divine_arsenal"
    if not divine_arsenal_dir.exists():
        print("❌ divine_arsenal directory not found!")
        print("Make sure you're running this from the project root.")
        sys.exit(1)

    # Change to divine_arsenal directory and run the enhanced launcher
    launcher_script = divine_arsenal_dir / "launch_enhanced.py"
    if not launcher_script.exists():
        print("❌ launch_enhanced.py not found in divine_arsenal directory!")
        sys.exit(1)

    print("✅ Found divine_arsenal system")
    print("🎮 Starting advanced SMITE 2 companion...")
    print()

    try:
        # Change to divine_arsenal directory and run the launcher
        os.chdir(divine_arsenal_dir)
        subprocess.run([sys.executable, "launch_enhanced.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting system: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
