import sqlite3
import os

DB_PATH = r'C:\sf_collab_db\sf_collab_dev.db'

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at {DB_PATH}")
    exit()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(conversation_participants)")
columns = [row[1] for row in cur.fetchall()]

if 'is_pinned' not in columns:
    cur.execute("ALTER TABLE conversation_participants ADD COLUMN is_pinned BOOLEAN NOT NULL DEFAULT 0")
    print("✅ Added is_pinned")

if 'pinned_at' not in columns:
    cur.execute("ALTER TABLE conversation_participants ADD COLUMN pinned_at DATETIME")
    print("✅ Added pinned_at")

conn.commit()
conn.close()
print("🚀 Migration complete!")