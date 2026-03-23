import sqlite3, glob
dbs = glob.glob('instance/*.db')
for db in dbs:
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_news_articles'")
    if cursor.fetchone():
        print('FOUND in: ' + db)
    conn.close()
print('Search done')
