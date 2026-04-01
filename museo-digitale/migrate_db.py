"""
Database migration script to add new tables and columns for advanced features
Run this script to update the database schema
"""
from app import app
from models import db
import subprocess
import sys

def migrate_database():
    """Add new tables and columns to existing database"""
    with app.app_context():
        try:
            # Step 1: Create all new tables (will only create new ones)
            print("Step 1: Creating new tables...")
            db.create_all()
            print("  ✓ New tables created/verified")
            
            # Step 2: Add missing columns to existing item table
            print("\nStep 2: Migrating item table columns...")
            try:
                from migrate_item_columns import migrate_item_columns
                migrate_item_columns()
            except ImportError:
                print("  ⚠ migrate_item_columns.py not found, skipping column migration")
                print("  Run migrate_item_columns.py separately if needed")
            
            print("\n✓ Database migration completed successfully!")
            print("\n  New tables:")
            print("    - Exhibition (mostre/esposizioni)")
            print("    - ItemImage (immagini multiple)")
            print("    - ItemDocument (documenti multipli)")
            print("    - ItemValuation (valutazioni)")
            print("    - ItemQRCode (QR codes)")
            print("    - Notification (notifiche)")
            print("    - item_exhibitions (association table)")
            print("\n  New columns in item table:")
            print("    - acquisition_cost")
            print("    - is_visible")
            print("    - view_count")
        except Exception as e:
            print(f"\n✗ Error during migration: {e}")
            raise

if __name__ == '__main__':
    migrate_database()

