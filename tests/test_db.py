#!/usr/bin/env python3
"""
Test database connection and basic operations
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test database connection and basic operations"""
    db_url = os.getenv('DATABASE_URL')
    
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    print("Testing database connection...")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Test 1: Check tables exist
        print("\nTesting table structure...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('organisations', 'reports', 'reporters', 'facilities')
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        print(f"Found {len(tables)} main tables: {[t[0] for t in tables]}")
        
        # Test 2: Insert and query a test organisation
        print("\nTesting INSERT operation...")
        cur.execute("""
            INSERT INTO organisations (name, type, contact_email, facilities)
            VALUES ('Test Water Utility', 'utility', 'contact@test.com', '[]'::jsonb)
            RETURNING id, name, type;
        """)
        org = cur.fetchone()
        print(f"Created test organisation: {org[1]} ({org[2]})")
        
        # Test 3: Query the organisation
        print("\nTesting SELECT operation...")
        cur.execute("""
            SELECT id, name, type, contact_email 
            FROM organisations 
            WHERE name = 'Test Water Utility';
        """)
        result = cur.fetchone()
        print(f"Retrieved organisation: {result[1]}")
        
        # Test 4: Test pgvector
        print("\nTesting pgvector functionality...")
        cur.execute("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname = 'vector';
        """)
        vector_ext = cur.fetchone()
        if vector_ext:
            print(f"pgvector {vector_ext[1]} is installed")
            
            # Test vector operations
            test_embedding = [0.1] * 384  # 384-dimensional vector
            cur.execute("""
                INSERT INTO reports (title, description, category, urgency, status, embedding)
                VALUES ('Test Report', 'This is a test', 'infrastructure', 'low', 'submitted', %s)
                RETURNING id, title;
            """, (test_embedding,))
            report = cur.fetchone()
            print(f"Created test report with embedding: {report[1]}")
            
            # Test similarity search
            cur.execute("""
                SELECT title, 1 - (embedding <=> %s::vector) as similarity
                FROM reports
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT 5;
            """, (test_embedding, test_embedding))
            similar = cur.fetchall()
            print(f"Similarity search works! Found {len(similar)} results")
        else:
            print("pgvector not found")
        
        # Cleanup test data
        print("\nCleaning up test data...")
        cur.execute("DELETE FROM reports WHERE title = 'Test Report';")
        cur.execute("DELETE FROM organisations WHERE name = 'Test Water Utility';")
        conn.commit()
        print("Test data cleaned up")
        
        cur.close()
        conn.close()
        
        print("\nAll database tests passed!")
        return True
        
    except Exception as e:
        print(f"\nError: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
