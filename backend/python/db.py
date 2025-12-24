"""
Database connection management for Dira
Provides connection pooling and context managers
"""

import os
from contextlib import contextmanager
from typing import Generator
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class Database:
    """Database connection manager with connection pooling"""
    
    _pool = None
    
    @classmethod
    def initialize(cls, min_conn=1, max_conn=10):
        """Initialize connection pool"""
        db_url = os.getenv('DATABASE_URL')
        
        if not db_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Heroku uses postgres:// but psycopg2 needs postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
        if cls._pool is None:
            cls._pool = psycopg2.pool.ThreadedConnectionPool(
                min_conn,
                max_conn,
                db_url
            )
            print(f"Database connection pool initialized ({min_conn}-{max_conn} connections)")
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool"""
        if cls._pool is None:
            cls.initialize()
        return cls._pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Return a connection to the pool"""
        if cls._pool:
            cls._pool.putconn(conn)
    
    @classmethod
    def close_all(cls):
        """Close all connections in the pool"""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            print("Database connection pool closed")

@contextmanager
def get_db_connection() -> Generator:
    """
    Context manager for database connections
    
    Usage:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM reports")
            results = cur.fetchall()
    """
    conn = Database.get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        Database.return_connection(conn)

@contextmanager
def get_db_cursor(dict_cursor=True) -> Generator:
    """
    Context manager for database cursor
    
    Args:
        dict_cursor: If True, returns results as dictionaries
    
    Usage:
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM reports")
            results = cur.fetchall()  # Returns list of dicts
    """
    conn = Database.get_connection()
    cursor_factory = RealDictCursor if dict_cursor else None
    cur = conn.cursor(cursor_factory=cursor_factory)
    
    try:
        yield cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        Database.return_connection(conn)

# Initialize on import
Database.initialize()
