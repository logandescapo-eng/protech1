"""
Database connection module
Handles PostgreSQL connections using psycopg2
"""

import psycopg2
from psycopg2 import pool, extras
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
import logging

logger = logging.getLogger(__name__)

# Connection pool (optional, but better for production)
connection_pool = None

def get_db_connection():
    """Get a database connection from the pool or create a new one"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def init_db_pool():
    """Initialize connection pool (optional optimization)"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # min and max connections
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
    except psycopg2.Error as e:
        logger.error(f"Connection pool initialization error: {e}")
        raise

def get_db_cursor(conn=None):
    """Get a database cursor with dict-like results"""
    if conn is None:
        conn = get_db_connection()
    return conn.cursor(cursor_factory=extras.RealDictCursor)
