#!/usr/bin/env python3
"""
Clear all organisations from the database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from db import get_db_cursor

def clear_organisations():
    """Delete all organisations"""
    print("⚠️  WARNING: This will delete ALL organisations and their related facilities/routes.")
    confirm = input("Are you sure you want to proceed? (yes/no): ")
    
    if confirm.lower() != "yes":
        print("Operation cancelled.")
        return

    print("🗑️  Clearing organisations...")
    
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM organisations;")
        count = cur.rowcount
        print(f"✅ Deleted {count} organisations.")

if __name__ == "__main__":
    clear_organisations()
