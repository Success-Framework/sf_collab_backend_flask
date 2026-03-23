from app import create_app
from app.extensions import db
from sqlalchemy import text, inspect

app = create_app()
with app.app_context():
    # 1. Create all missing tables (like startup_views)
    db.create_all()
    
    # 2. Add missing columns to existing tables
    engine = db.engine
    inspector = inspect(engine)
    
    updates = [
        ('startups', 'lifecycle_state', "'idea'"),
        ('ideas', 'vision_state', "'draft'"),
        ('users', 'storage_used_mb', '0.0')
    ]
    
    for table, column, default in updates:
        existing_columns = [c['name'] for c in inspector.get_columns(table)]
        if column not in existing_columns:
            print(f"Adding {column} to {table}...")
            db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} TEXT DEFAULT {default}"))
    
    db.session.commit()
    print("✅ Database synced and repaired successfully!")
