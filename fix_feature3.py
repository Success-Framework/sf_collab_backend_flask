import sqlite3
import os

db_path = 'C:/sf_collab_db/sf_collab_dev.db'

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cur = conn.cursor()

def col_exists(table, col):
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())

def table_exists(table):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None

# Apply Alterations
if not col_exists('conversation_participants', 'is_archived'):
    cur.execute('ALTER TABLE conversation_participants ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0')
    print('+ is_archived added')

if not col_exists('conversation_participants', 'archived_at'):
    cur.execute('ALTER TABLE conversation_participants ADD COLUMN archived_at DATETIME')
    print('+ archived_at added')

# Tables to create
tables = {
    'message_stars': 'CREATE TABLE message_stars (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, message_id INTEGER NOT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id, message_id))',
    'pinned_messages': 'CREATE TABLE pinned_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id INTEGER NOT NULL, message_id INTEGER NOT NULL, pinned_by INTEGER NOT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(conversation_id, message_id))',
    'message_tasks': 'CREATE TABLE message_tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, message_id INTEGER NOT NULL, conversation_id INTEGER NOT NULL, due_date DATETIME, note TEXT, is_done INTEGER NOT NULL DEFAULT 0, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id, message_id))'
}

for name, ddl in tables.items():
    if not table_exists(name):
        cur.execute(ddl)
        print(f'+ {name} created')

conn.commit()
conn.close()
print('Done! Feature 3 is ready.')