import sqlite3

DB_PATH = 'instance/sf_collab_dev.db'

migrations = [
    ('startups', 'execution_score', 'FLOAT DEFAULT 0.0'),
    ('startups', 'milestones_completed', 'INTEGER DEFAULT 0'),
    ('startups', 'milestones_total', 'INTEGER DEFAULT 0'),
    ('startups', 'last_activity_at', 'DATETIME'),
    ('startups', 'activity_score', 'FLOAT DEFAULT 0.0'),
    ('startups', 'lifecycle_state', 'VARCHAR(50)'),
    ('startups', 'crowdfunding_unlocked', 'BOOLEAN DEFAULT 0'),
    ('startups', 'crowdfunding_unlocked_at', 'DATETIME'),
    ('ai_news_articles', 'summary', 'TEXT'),
    ('ai_news_articles', 'author', 'VARCHAR(255)'),
    ('ai_news_articles', 'image_url', 'TEXT'),
    ('ai_news_articles', 'source_label', 'VARCHAR(100)'),
    ('ai_news_articles', 'impact_score', 'INTEGER DEFAULT 5'),
    ('ai_news_articles', 'scraped_at', 'DATETIME'),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for table, column, col_type in migrations:
    try:
        cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}')
        print('Added ' + table + '.' + column)
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e):
            print('Skipped ' + table + '.' + column + ' (already exists)')
        else:
            print('ERROR on ' + table + '.' + column + ': ' + str(e))

conn.commit()
conn.close()
print('Done!')
