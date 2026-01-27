from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # This adds the missing column to your existing table
    with db.engine.connect() as conn:
        conn.execute(text("ALTER TABLE ideas ADD COLUMN image_url VARCHAR(255)"))
        conn.commit()
    print("Database column 'image_url' added successfully!")
