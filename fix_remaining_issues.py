#!/usr/bin/env python3
"""
Quick fix script for remaining code audit warnings
"""

import os
import re
from pathlib import Path

def fix_bare_excepts():
    """Fix bare except clauses."""
    print("🔧 Fixing bare except clauses...")
    
    files_to_fix = [
        'code_audit_fix.py',
        'smite2_update_system.py',
        'divine_arsenal/backend/patch_enhancer.py',
        'divine_arsenal/backend/user_auth.py',
        'divine_arsenal/backend/scrapers/tracker.py',
        'divine_arsenal/backend/scrapers/wiki_smite2.py'
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace bare except with specific exception
                if 'except:' in content:
                    content = content.replace('except:', 'except Exception:')
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Fixed bare except in {file_path}")
                    
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")

def fix_unused_imports():
    """Fix unused imports."""
    print("📚 Fixing unused imports...")
    
    files_to_fix = [
        'divine_arsenal_status.py',
        'divine_arsenal/backend/config.py',
        'divine_arsenal/backend/data_loader.py'
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if os is imported but not used
                if 'import os' in content and 'os.' not in content:
                    # Remove the import line
                    lines = content.split('\n')
                    new_lines = []
                    for line in lines:
                        if not line.strip().startswith('import os') and not line.strip().startswith('import os as'):
                            new_lines.append(line)
                    
                    content = '\n'.join(new_lines)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Removed unused os import from {file_path}")
                    
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")

def create_missing_init_files():
    """Create missing __init__.py files."""
    print("📁 Creating missing __init__.py files...")
    
    dirs_to_fix = [
        'divine_arsenal',
        'divine_arsenal/tests'
    ]
    
    for dir_path in dirs_to_fix:
        if os.path.exists(dir_path):
            init_path = os.path.join(dir_path, '__init__.py')
            if not os.path.exists(init_path):
                try:
                    with open(init_path, 'w', encoding='utf-8') as f:
                        f.write("# Auto-generated __init__.py file\n")
                    print(f"✅ Created {init_path}")
                except Exception as e:
                    print(f"❌ Error creating {init_path}: {e}")

def main():
    """Main function."""
    print("🔧 Fixing remaining code audit warnings...")
    print("=" * 50)
    
    fix_bare_excepts()
    fix_unused_imports()
    create_missing_init_files()
    
    print("\n✅ All fixes applied!")
    print("   Run the code audit again to verify improvements.")

if __name__ == "__main__":
    main() 