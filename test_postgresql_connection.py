#!/usr/bin/env python3
"""
Test PostgreSQL Connection and Data
Direct test to see what's actually in the database
"""

import os
import sys
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import database configuration
from divine_arsenal.backend.database_config import get_database_config

# Initialize Flask app
app = Flask(__name__)

# Load database configuration
db_config = get_database_config()
flask_config = db_config.get_flask_config()

# Apply configuration to Flask app
for key, value in flask_config.items():
    app.config[key] = value

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models (simplified)
class God(db.Model):
    __tablename__ = 'gods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(50))

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    cost = db.Column(db.Integer, default=0)

def main():
    """Test PostgreSQL connection and list data."""
    print("🔍 POSTGRESQL CONNECTION TEST")
    print("=" * 50)
    
    print(f"Database Type: {db_config.get_database_type()}")
    print(f"Database URI: {db_config.get_database_uri()}")
    print()
    
    try:
        with app.app_context():
            # Test connection
            result = db.session.execute(db.text('SELECT 1')).scalar()
            print(f"✅ PostgreSQL Connection: {result}")
            
            # Count gods
            gods_count = God.query.count()
            print(f"✅ Total Gods: {gods_count}")
            
            # List first 10 gods
            gods = God.query.limit(10).all()
            print("📋 First 10 Gods:")
            for god in gods:
                print(f"   - {god.name} ({god.role})")
            
            # Count items
            items_count = Item.query.count()
            print(f"✅ Total Items: {items_count}")
            
            # List first 10 items
            items = Item.query.limit(10).all()
            print("📋 First 10 Items:")
            for item in items:
                print(f"   - {item.name} ({item.cost}g)")
            
            # Test specific god lookup
            zeus = God.query.filter_by(name='Zeus').first()
            if zeus:
                print(f"✅ Zeus Found: {zeus.name} ({zeus.role})")
            else:
                print("❌ Zeus NOT found")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 