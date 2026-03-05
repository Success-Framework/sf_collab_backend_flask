import sqlite3
import os

# List of possible locations for your DB
paths = ['sf_collab_dev.db', 'instance/sf_collab_dev.db', 'C:/sf_collab_db/sf_collab_dev.db']

for db_path in paths:
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            
            # 1. Check user_wallets for missing columns
            cur.execute("PRAGMA table_info(user_wallets)")
            cols = [column[1] for column in cur.fetchall()]
            
            if cols: # If table exists
                needed_cols = [
                    ('credits', 'INTEGER DEFAULT 0'),
                    ('sf_coins', 'INTEGER DEFAULT 0'),
                    ('premium_gems', 'INTEGER DEFAULT 0')
                ]
                
                for col_name, col_type in needed_cols:
                    if col_name not in cols:
                        cur.execute(f'ALTER TABLE user_wallets ADD COLUMN {col_name} {col_type}')
                        print(f"✅ Added '{col_name}' to {db_path}")
                
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Error in {db_path}: {e}")
    else:
        print(f"📂 Not found: {db_path}")

print("🚀 Database check complete!")