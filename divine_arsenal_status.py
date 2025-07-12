#!/usr/bin/env python3
"""
Divine Arsenal System Status Checker
Checks the health and structure of the divine-arsenal system after cleanup
"""

import sys
from pathlib import Path


def check_system_status():
    """Check the divine_arsenal system status."""

    print("🔍 DIVINE ARSENAL SYSTEM STATUS CHECK")
    print("=" * 50)

    divine_path = Path("divine_arsenal")
    backend_path = divine_path / "backend"

    if not divine_path.exists():
        print("❌ divine_arsenal directory not found!")
        return False

    if not backend_path.exists():
        print("❌ backend directory not found!")
        return False

    # Check essential files
    essential_files = {
        "app.py": "Main Flask application",
        "database.py": "Database layer",
        "advanced_build_optimizer.py": "Advanced build optimizer",
        "build_explainer.py": "Build explanation system",
        "statistical_analyzer.py": "Statistical analysis",
        "player_performance_integrator.py": "Player performance system",
        "god_data.py": "God data access",
        "item_data.py": "Item data access",
        "divine_arsenal.db": "Main database",
    }

    print("✅ ESSENTIAL FILES CHECK:")
    missing_files = []
    total_size = 0

    for file_name, description in essential_files.items():
        file_path = backend_path / file_name
        if file_path.exists():
            size = file_path.stat().st_size / 1024  # KB
            total_size += size
            print(f"  ✅ {file_name:<35} ({size:6.1f} KB) - {description}")
        else:
            print(f"  ❌ {file_name:<35} (MISSING) - {description}")
            missing_files.append(file_name)

    # Check directories
    essential_dirs = {"scrapers": "Data scraping modules", "templates": "Web interface templates"}

    print(f"\n✅ ESSENTIAL DIRECTORIES CHECK:")
    missing_dirs = []

    for dir_name, description in essential_dirs.items():
        dir_path = backend_path / dir_name
        if dir_path.exists():
            file_count = len(list(dir_path.glob("*")))
            print(f"  ✅ {dir_name:<15} ({file_count} files) - {description}")
        else:
            print(f"  ❌ {dir_name:<15} (MISSING) - {description}")
            missing_dirs.append(dir_name)

    # Check data directory
    data_path = divine_path / "data"
    if data_path.exists():
        gods_file = data_path / "gods.json"
        items_file = data_path / "items.json"
        gods_exists = gods_file.exists()
        items_exists = items_file.exists()
        print(f"\n✅ DATA FILES CHECK:")
        print(f"  {'✅' if gods_exists else '❌'} gods.json - Gods data")
        print(f"  {'✅' if items_exists else '❌'} items.json - Items data")
    else:
        print(f"\n❌ DATA DIRECTORY MISSING")

    # System summary
    print(f"\n📊 SYSTEM SUMMARY:")
    print(f"  • Total essential files size: {total_size:.1f} KB")
    print(f"  • Missing files: {len(missing_files)}")
    print(f"  • Missing directories: {len(missing_dirs)}")

    if missing_files or missing_dirs:
        print(f"\n⚠️  ISSUES FOUND:")
        for file in missing_files:
            print(f"    • Missing file: {file}")
        for dir in missing_dirs:
            print(f"    • Missing directory: {dir}")
        return False
    else:
        print(f"\n🎉 SYSTEM HEALTHY!")
        print(f"✅ All essential components present")
        print(f"🚀 Ready to launch with: python launch_divine_arsenal.py")
        return True


def check_import_health():
    """Check for potential import issues."""
    print(f"\n🔍 IMPORT HEALTH CHECK:")

    backend_path = Path("divine_arsenal/backend")

    # Check if scrapers has __init__.py
    scrapers_init = backend_path / "scrapers" / "__init__.py"
    if not scrapers_init.exists():
        print(f"  ⚠️  scrapers/__init__.py missing - may cause import errors")
        return False

    print(f"  ✅ Import structure looks good")
    return True


def show_clean_structure():
    """Show the expected clean structure."""
    print(f"\n🎯 EXPECTED CLEAN STRUCTURE:")
    print(f"divine_arsenal/")
    print(f"├── backend/")
    print(f"│   ├── app.py                          # Main Flask app")
    print(f"│   ├── database.py                     # Database layer")
    print(f"│   ├── advanced_build_optimizer.py     # Advanced optimizer")
    print(f"│   ├── build_explainer.py              # Build explanations")
    print(f"│   ├── statistical_analyzer.py         # Statistics")
    print(f"│   ├── player_performance_integrator.py # Player system")
    print(f"│   ├── multi_mode_optimizer.py         # Multi-mode support")
    print(f"│   ├── god_data.py / item_data.py      # Data access")
    print(f"│   ├── scrapers/                       # Data scrapers")
    print(f"│   ├── templates/                      # Web interface")
    print(f"│   └── divine_arsenal.db               # Main database")
    print(f"├── data/")
    print(f"│   ├── gods.json                       # Gods data")
    print(f"│   └── items.json                      # Items data")
    print(f"├── launch_enhanced.py                  # System launcher")
    print(f"└── docs/                               # Documentation")


if __name__ == "__main__":
    healthy = check_system_status()
    imports_ok = check_import_health()
    show_clean_structure()

    if healthy and imports_ok:
        print(f"\n🎉 SYSTEM STATUS: EXCELLENT")
        print(f"💡 Your divine_arsenal system is clean and ready!")
    else:
        print(f"\n⚠️  SYSTEM STATUS: NEEDS ATTENTION")
        print(f"🔧 Some issues found that may need fixing")
