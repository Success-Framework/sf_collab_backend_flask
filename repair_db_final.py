import sqlite3
import os

# Find the database in instance/ or root
db_paths = [os.path.abspath(os.path.join(r, f)) for r, d, fs in os.walk('.') 
            for f in fs if f.endswith('.db') and '.venv' not in r]
db_path = db_paths[0]
print(f"Targeting Database: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

migrations = [
    ('startups', 'lifecycle_state', 'VARCHAR(50) DEFAULT "active"'),
    ('startups', 'execution_score', 'FLOAT DEFAULT 0.0'),
    ('startups', 'milestones_completed', 'INTEGER DEFAULT 0'),
    ('startups', 'milestones_total', 'INTEGER DEFAULT 0'),
    ('startups', 'last_activity_at', 'TIMESTAMP'),
    ('startups', 'activity_score', 'FLOAT DEFAULT 0.0'),
    ('startups', 'crowdfunding_unlocked', 'BOOLEAN DEFAULT 0'),
    ('startups', 'crowdfunding_unlocked_at', 'TIMESTAMP'),
    ('ideas', 'vision_state', 'VARCHAR(50) DEFAULT "public"'),
    ('ideas', 'readiness_score', 'FLOAT DEFAULT 0.0'),
    ('ideas', 'readiness_breakdown', 'JSON'),
    ('ideas', 'problem_statement', 'TEXT'),
    ('ideas', 'outcome_goal', 'TEXT'),
    ('ideas', 'risk_level', 'VARCHAR(20) DEFAULT "medium"'),
    ('ideas', 'required_roles', 'JSON'),
    ('ideas', 'roadmap_items', 'JSON'),
]

# Run migrations
for table, col, typedef in migrations:
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cur.fetchall()}
    if col not in existing:
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}")
            print(f"  ✅ ADDED: {table}.{col}")
        except Exception as e:
            print(f"  ❌ ERROR on {table}.{col}: {e}")
    else:
        print(f"  🟡 EXISTS: {table}.{col}")

# Update the state logic
cur.execute("UPDATE startups SET lifecycle_state = 'founder_only' WHERE member_count <= 1")
print(f"  🔄 Updated {cur.rowcount} startups to founder_only.")

conn.commit()
conn.close()
print("\n🎉 Database is now fully synchronized with your models!")
