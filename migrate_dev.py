import sqlite3

DB_PATH = 'instance/sf_collab_dev.db'

migrations = [
    ('ideas', 'readiness_score', 'FLOAT DEFAULT 0.0'),
    ('ideas', 'readiness_breakdown', 'TEXT'),
    ('ideas', 'problem_statement', 'TEXT'),
    ('ideas', 'outcome_goal', 'TEXT'),
    ('ideas', 'risk_level', 'VARCHAR(50)'),
    ('ideas', 'required_roles', 'TEXT'),
    ('ideas', 'roadmap_items', 'TEXT'),
    ('ideas', 'vision_state', 'TEXT'),
    ('ai_news_articles', 'summary', 'TEXT'),
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
