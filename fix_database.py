"""
Database Fix Script for SF Collab
Adds the missing 'visible_by' column to the tasks table
"""

import sqlite3
import os
from pathlib import Path

def find_db_files(start_path):
    """Find all .db files in the project"""
    db_files = []
    for root, dirs, files in os.walk(start_path):
        # Skip virtual environment and cache directories
        dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '__pycache__', 'node_modules']]
        for file in files:
            if file.endswith('.db'):
                db_files.append(os.path.join(root, file))
    return db_files

def check_column_exists(db_path, table_name, column_name):
    """Check if a column exists in a table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()
        return column_name in columns
    except Exception as e:
        print(f"Error checking column: {e}")
        return False

def add_column(db_path, table_name, column_name, column_type="TEXT"):
    """Add a column to a table if it doesn't exist"""
    try:
        if check_column_exists(db_path, table_name, column_name):
            print(f"  ✓ Column '{column_name}' already exists in '{table_name}'")
            return True
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        conn.commit()
        conn.close()
        print(f"  ✓ Added column '{column_name}' to '{table_name}'")
        return True
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print(f"  ⚠ Table '{table_name}' doesn't exist in this database")
        else:
            print(f"  ✗ Error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("SF Collab Database Fix Script")
    print("=" * 60)
    
    # Get current directory or use provided path
    current_dir = os.getcwd()
    print(f"\nSearching for databases in: {current_dir}")
    
    # Find all database files
    db_files = find_db_files(current_dir)
    
    if not db_files:
        print("\n❌ No .db files found!")
        print("Make sure you're running this script from your backend folder.")
        return
    
    print(f"\nFound {len(db_files)} database file(s):")
    for i, db in enumerate(db_files, 1):
        print(f"  {i}. {db}")
    
    # Process each database
    print("\n" + "-" * 60)
    print("Attempting to fix each database...")
    print("-" * 60)
    
    for db_path in db_files:
        print(f"\n📁 Processing: {db_path}")
        
        # Add visible_by column to tasks table
        add_column(db_path, "tasks", "visible_by", "TEXT")
    
    print("\n" + "=" * 60)
    print("✅ Done! Please restart your Flask server and try again.")
    print("=" * 60)

if __name__ == "__main__":
    main()