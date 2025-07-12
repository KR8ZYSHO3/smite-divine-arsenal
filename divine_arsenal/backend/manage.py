#!/usr/bin/env python3
"""
Manage Script for Flask-Migrate Commands
Runs database migrations and other CLI tasks
"""

import os
import sys

# Add the backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask.cli import FlaskGroup
from app_with_migrations import app

# Set up Flask CLI group
cli = FlaskGroup(app=app)

if __name__ == '__main__':
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Add backend to PYTHONPATH
    sys.path.insert(0, os.path.abspath('.'))
    
    print("🚀 SMITE 2 DIVINE ARSENAL - MIGRATION MANAGER")
    print("=" * 60)
    print("Available commands:")
    print("  python manage.py db init - Initialize migrations")
    print("  python manage.py db migrate -m 'Initial migration' - Create migration script")
    print("  python manage.py db upgrade - Apply migrations")
    print("  python manage.py db downgrade - Revert last migration (use with caution)")
    print("  python manage.py db current - Show current revision")
    print("  python manage.py db history - Show migration history")
    print()
    
    cli() 