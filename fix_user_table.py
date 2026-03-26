import sqlite3
import os

DB_PATH = r'C:\sf_collab_db\sf_collab_dev.db'

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at {DB_PATH}")
    exit()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get existing columns in the users table
cur.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cur.fetchall()]

# List of columns that might be missing based on your logs
missing_cols = [
    ('storage_used_mb', 'FLOAT DEFAULT 0.0'),
    ('max_storage_mb', 'FLOAT DEFAULT 100.0'),
    ('bio', 'TEXT'),
    ('profile_pic', 'TEXT'),
    ('banner_pic', 'TEXT')
]

for col_name, col_type in missing_cols:
    if col_name not in columns:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"✅ Added '{col_name}' to users table.")
        except Exception as e:
            print(f"⚠️ Could not add {col_name}: {e}")

conn.commit()
conn.close()
print("🚀 Users table is now up to date!")