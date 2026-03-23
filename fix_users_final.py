import sqlite3
import os

DB_PATH = r'C:\sf_collab_db\sf_collab_dev.db'

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at {DB_PATH}")
    exit()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get existing columns
cur.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cur.fetchall()]

# List of missing columns based on your error logs
required_cols = [
    ('last_seen', 'DATETIME'),
    ('storage_used_mb', 'FLOAT DEFAULT 0.0'),
    ('max_storage_mb', 'FLOAT DEFAULT 100.0'),
    ('total_revenue', 'FLOAT DEFAULT 0.0'),
    ('satisfaction_percentage', 'FLOAT DEFAULT 0.0'),
    ('active_startups_count', 'INTEGER DEFAULT 0'),
    ('profile_picture', 'TEXT'),
    ('profile_bio', 'TEXT'),
    ('profile_company', 'TEXT'),
    ('profile_social_links', 'TEXT'),
    ('profile_country', 'TEXT'),
    ('profile_city', 'TEXT'),
    ('profile_timezone', 'TEXT'),
    ('pref_email_notifications', 'BOOLEAN DEFAULT 1'),
    ('pref_push_notifications', 'BOOLEAN DEFAULT 1'),
    ('pref_privacy', 'TEXT DEFAULT "public"'),
    ('pref_language', 'TEXT DEFAULT "en"'),
    ('pref_theme', 'TEXT DEFAULT "light"'),
    ('notif_new_comments', 'BOOLEAN DEFAULT 1'),
    ('notif_new_likes', 'BOOLEAN DEFAULT 1'),
    ('notif_new_suggestions', 'BOOLEAN DEFAULT 1'),
    ('notif_join_requests', 'BOOLEAN DEFAULT 1'),
    ('notif_approvals', 'BOOLEAN DEFAULT 1')
]

for col_name, col_type in required_cols:
    if col_name not in columns:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"✅ Added '{col_name}'")
        except Exception as e:
            print(f"⚠️ Skipping {col_name}: {e}")

conn.commit()
conn.close()
print("🚀 Migration complete! All profile and notification columns are ready.")