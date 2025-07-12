#!/usr/bin/env python3
"""
Create Community Tables in PostgreSQL
Simple script to create community tables without migrations
"""

import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_with_migrations import app, db

def create_community_tables():
    """Create all community tables in PostgreSQL."""
    print("🗄️ Creating community tables in PostgreSQL...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Community tables created successfully!")
        
        # Verify tables exist
        from sqlalchemy import text
        result = db.session.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """))
        
        tables = [row[0] for row in result]
        print(f"📊 Tables in database: {', '.join(tables)}")
        
        # Check for community tables specifically
        community_tables = ['users', 'chat_messages', 'parties']
        for table in community_tables:
            if table in tables:
                print(f"✅ {table} table exists")
            else:
                print(f"❌ {table} table missing")

if __name__ == "__main__":
    # Set database URL
    os.environ['DATABASE_URL'] = "postgresql://divine_arsenal_db_user:PHc5f6cz2mPKBlfhZhe6mRgvxDNsRkmH@dpg-d1op9jbipnbc73fa7gg0-a.oregon-postgres.render.com/divine_arsenal_db"
    
    create_community_tables()
    print("🎉 Database setup complete!") 