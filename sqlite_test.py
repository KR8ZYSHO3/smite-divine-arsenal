import sqlite3
import os

db_path = os.path.abspath("divine_arsenal/backend/divine_arsenal.db")
print(f"Testing SQLite DB at: {db_path}")

# Ensure directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()
    conn.close()
    print("✅ Database created and writable!")
except Exception as e:
    print(f"❌ Database error: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Database file exists: {os.path.exists(db_path)}") 