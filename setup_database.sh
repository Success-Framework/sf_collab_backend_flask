#!/bin/bash

# Database Setup Script for SF Collab Backend
# This script creates all database tables from SQLAlchemy models

set -e  # Exit on error

echo "Starting database setup..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run 'python -m venv venv' first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set database URL (modify if needed)
export DATABASE_URL="${DATABASE_URL:-mysql+pymysql://sfcollab:sfcollab_pass@localhost:3306/defaultdb}"

echo "Using database: $DATABASE_URL"

# Create all tables
python << EOF
from app import create_app, db
from app.models.activity import Activity

app = create_app()
with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("✓ All tables created successfully")
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"✓ Total tables: {len(tables)}")
    print(f"✓ Tables: {', '.join(sorted(tables))}")
EOF

echo "Database setup complete!"
