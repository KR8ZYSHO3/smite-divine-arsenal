#!/usr/bin/env python3
"""
Enhanced launcher for Smite 2 Divine Arsenal
Includes all advanced features and comprehensive system capabilities
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def main():
    """Launch the enhanced SMITE 2 Divine Arsenal application."""

    print("🚀 LAUNCHING SMITE 2 DIVINE ARSENAL - ENHANCED SYSTEM")
    print("=" * 60)
    print("✨ Advanced Features:")
    print("  • Advanced Build Optimization with Item Synergy Analysis")
    print("  • Statistical Analysis & Meta Intelligence")
    print("  • Player Performance Integration & Calibration")
    print("  • Build Explanation System with AI-powered insights")
    print("  • Multi-Mode Optimizer (Conquest, Arena, Joust, etc.)")
    print("  • Real-time Data Collection & Patch Analysis")
    print("  • Enhanced Web Dashboard with Modern UI")
    print()

    # Ensure we're in the right directory
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir / "backend"

    print(f"📁 Working directory: {backend_dir}")

    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return

    app_file = backend_dir / "app.py"
    if not app_file.exists():
        print("❌ Backend app not found!")
        return

    print("✅ Enhanced backend app found")
    print("🌐 Starting Flask server with advanced features...")
    print("📍 API will be available at: http://localhost:5002")
    print("🔧 API endpoints available at: http://localhost:5002/api/")
    print("🏁 Press Ctrl+C to stop the server")
    print("-" * 60)

    try:
        # Change to backend directory and run
        os.chdir(backend_dir)

        # Set environment variable for port
        env = os.environ.copy()
        env["FLASK_PORT"] = "5000"

        # Launch the enhanced server
        result = subprocess.run([sys.executable, "app.py"], env=env, check=True)

    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
