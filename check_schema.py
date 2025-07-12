#!/usr/bin/env python3
"""
Check database schema and data
"""

import os
import sqlite3


def check_database(db_path):
    print(f"🔍 CHECKING DATABASE: {db_path}")
    print("=" * 50)

    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("⚠️  Warning: No tables found in database. Schema may not be initialized.")
            return
        else:
            print(f"📋 Tables found: {[table[0] for table in tables]}")
            for table in tables:
                print(f"   ✅ Table {table[0]}: OK")

        # Check gods table schema
        if ("gods",) in tables:
            print("\n🏛️ GODS TABLE SCHEMA:")
            cursor.execute("PRAGMA table_info(gods)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")

            # Check gods data
            cursor.execute("SELECT COUNT(*) FROM gods")
            god_count = cursor.fetchone()[0]
            print(f"\n📊 Gods in database: {god_count}")

            if god_count > 0:
                cursor.execute("SELECT name, role FROM gods LIMIT 5")
                gods = cursor.fetchall()
                print("First 5 gods:")
                for god in gods:
                    print(f"  {god[0]} ({god[1]})")
            else:
                print("⚠️  No gods found in database. Run sync_smite2_data.py to populate.")

        # Check items table schema
        if ("items",) in tables:
            print("\n⚔️ ITEMS TABLE SCHEMA:")
            cursor.execute("PRAGMA table_info(items)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")

            # Check items data
            cursor.execute("SELECT COUNT(*) FROM items")
            item_count = cursor.fetchone()[0]
            print(f"\n📦 Items in database: {item_count}")

            if item_count > 0:
                cursor.execute("SELECT name, category, tags FROM items LIMIT 5")
                items = cursor.fetchall()
                print("First 5 items:")
                for item in items:
                    print(f"  {item[0]} | Category: {item[1]} | Tags: {item[2]}")
            else:
                print("⚠️  No items found in database. Run sync_smite2_data.py to populate.")

        conn.close()

    except Exception as e:
        print(f"❌ Error checking database: {e}")


def main():
    print("🔍 DATABASE SCHEMA CHECKER")
    print("=" * 50)

    # Check both database files
    check_database("divine_arsenal.db")
    print("\n" + "=" * 50 + "\n")
    check_database("divine-arsenal/backend/divine_arsenal.db")


if __name__ == "__main__":
    main()
