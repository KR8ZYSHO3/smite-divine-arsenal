#!/usr/bin/env python3
"""
Divine Arsenal Performance Launcher
Optimized launcher for better performance and resource usage
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Divine Arsenal system with performance optimizations."""

    print("⚡ DIVINE ARSENAL - PERFORMANCE OPTIMIZED")
    print("=" * 50)
    print("🔥 Features:")
    print("  • Lightweight startup (components loaded on demand)")
    print("  • No unnecessary Chrome/WebDriver processes")
    print("  • Optimized resource usage")
    print("  • Fast server startup")
    print()

    # Check if divine_arsenal directory exists
    divine_arsenal_dir = Path(__file__).parent / "divine_arsenal"
    if not divine_arsenal_dir.exists():
        print("❌ divine_arsenal directory not found!")
        print("Make sure you're running this from the project root.")
        sys.exit(1)

    # Check for the lightweight app
    backend_dir = divine_arsenal_dir / "backend"
    app_file = backend_dir / "app_lightweight.py"

    if not app_file.exists():
        print("❌ app_lightweight.py not found in backend directory!")
        sys.exit(1)

    print("✅ Found performance-optimized backend")
    print("🚀 Starting lightweight SMITE 2 companion...")
    print("📍 Will be available at: http://localhost:5000")
    print("🏁 Press Ctrl+C to stop the server")
    print()

    try:
        # Change to backend directory and run the lightweight app
        os.chdir(backend_dir)
        subprocess.run([sys.executable, "app_lightweight.py"], check=True)
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
