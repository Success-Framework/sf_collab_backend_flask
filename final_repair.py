from app import create_app
from app.extensions import db
from sqlalchemy import text, inspect

app = create_app()
with app.app_context():
    # 1. Ensure all tables (like startup_views) exist
    db.create_all()
    
    engine = db.engine
    inspector = inspect(engine)
    
    # Define all possible missing columns identified in your logs
    updates = {
        'startups': [
            ('lifecycle_state', 'TEXT DEFAULT "idea"'),
            ('execution_score', 'FLOAT DEFAULT 0.0')
        ],
        'ideas': [
            ('vision_state', 'TEXT DEFAULT "draft"'),
            ('readiness_score', 'FLOAT DEFAULT 0.0'),
            ('readiness_breakdown', 'TEXT DEFAULT "{}"'),
            ('risk_level', 'TEXT DEFAULT "medium"')
        ],
        'users': [
            ('storage_used_mb', 'FLOAT DEFAULT 0.0')
        ]
    }
    
    for table, columns in updates.items():
        if table in inspector.get_table_names():
            existing = [c['name'] for c in inspector.get_columns(table)]
            for col_name, col_def in columns:
                if col_name not in existing:
                    print(f"Adding {col_name} to {table}...")
                    try:
                        db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}"))
                    except Exception as e:
                        print(f"Could not add {col_name}: {e}")
    
    db.session.commit()
    print("✅ Database sync complete. All missing columns added!")
