import sqlite3
import os

# Your app is using the DB in the current folder based on logs
db_path = 'sf_collab_dev.db'

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # --- Fix user_wallets ---
        cur.execute("PRAGMA table_info(user_wallets)")
        wallet_cols = [column[1] for column in cur.fetchall()]
        if wallet_cols and 'credits' not in wallet_cols:
            cur.execute('ALTER TABLE user_wallets ADD COLUMN credits INTEGER DEFAULT 0')
            print("✅ Added 'credits' to user_wallets")

        # --- Fix idea_comments ---
        cur.execute("PRAGMA table_info(idea_comments)")
        comment_cols = [column[1] for column in cur.fetchall()]
        if comment_cols and 'suggestion' not in comment_cols:
            cur.execute('ALTER TABLE idea_comments ADD COLUMN suggestion TEXT')
            print("✅ Added 'suggestion' to idea_comments")
            
        conn.commit()
        conn.close()
        print("🚀 Database sync complete!")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print(f"📂 DB file {db_path} not found in this folder.")