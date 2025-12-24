#!/usr/bin/env python3
"""
Database setup script for Dira
Connects to Heroku PostgreSQL and creates the schema
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Get database URL from environment"""
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        print("Please run: heroku config:get DATABASE_URL -a dira-platform-backend")
        exit(1)
    
    # Heroku uses postgres:// but psycopg2 needs postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    return db_url

def run_schema():
    """Run the schema.sql file"""
    db_url = get_database_url()
    
    print(f"Connecting to database...")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print("Executing schema setup...")
        cur.execute(schema_sql)
        conn.commit()
        
        print("✅ Schema created successfully!")
        
        # Verify tables were created
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        print(f"\n📋 Tables created ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if vector extension is enabled
        cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if cur.fetchone():
            print("\n✅ pgvector extension is enabled")
        else:
            print("\n⚠️  pgvector extension not found - trying to enable it...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            print("✅ pgvector extension enabled")
        
        cur.close()
        conn.close()
        
        print("\n🎉 Database setup complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

if __name__ == "__main__":
    run_schema()
