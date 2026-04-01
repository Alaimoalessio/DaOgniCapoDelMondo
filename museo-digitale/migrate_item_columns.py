"""
Migration script to add new columns to existing item table
This adds: acquisition_cost, is_visible, view_count
"""
from app import app
from models import db
import sqlite3
import os

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def migrate_item_columns():
    """Add missing columns to item table"""
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        
        if not db_uri.startswith('sqlite:///'):
            print("✗ This migration only works with SQLite")
            return
        
        db_path = db_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.config['BASE_DIR'], db_path)
        
        if not os.path.exists(db_path):
            print(f"✗ Database file not found: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check existing columns
            columns_to_add = []
            
            if not check_column_exists(cursor, 'item', 'acquisition_cost'):
                columns_to_add.append(('acquisition_cost', 'NUMERIC(12, 2)'))
                print("  - acquisition_cost: MISSING")
            else:
                print("  - acquisition_cost: EXISTS")
            
            if not check_column_exists(cursor, 'item', 'is_visible'):
                columns_to_add.append(('is_visible', 'BOOLEAN DEFAULT 1'))
                print("  - is_visible: MISSING")
            else:
                print("  - is_visible: EXISTS")
            
            if not check_column_exists(cursor, 'item', 'view_count'):
                columns_to_add.append(('view_count', 'INTEGER DEFAULT 0'))
                print("  - view_count: MISSING")
            else:
                print("  - view_count: EXISTS")
            
            # Add missing columns
            if columns_to_add:
                print(f"\nAdding {len(columns_to_add)} column(s)...")
                for col_name, col_type in columns_to_add:
                    try:
                        cursor.execute(f"ALTER TABLE item ADD COLUMN {col_name} {col_type}")
                        print(f"  ✓ Added column: {col_name}")
                    except sqlite3.OperationalError as e:
                        if "duplicate column" in str(e).lower():
                            print(f"  ⚠ Column {col_name} already exists (skipping)")
                        else:
                            raise
                
                conn.commit()
                print("\n✓ Migration completed successfully!")
            else:
                print("\n✓ All columns already exist. No migration needed.")
        
        except Exception as e:
            conn.rollback()
            print(f"\n✗ Error during migration: {e}")
            raise
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_item_columns()

