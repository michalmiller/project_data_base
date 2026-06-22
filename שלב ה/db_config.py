"""
Database configuration and connection module.
"""
import psycopg2
from psycopg2 import sql, extras

DB_CONFIG = {
    "host": "localhost",
    "database": "integrated_db_stage3",
    "user": "postgres",
    "password": "123456",
    "port": "5432"
}


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


def execute_query(query, params=None, fetch=True):
    """Execute a query and optionally return results."""
    conn = get_connection()
    conn.autocommit = True
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()
        return None
    except Exception as e:
        raise e
    finally:
        conn.close()


def execute_modify(query, params=None):
    """Execute INSERT/UPDATE/DELETE and return affected rows."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def call_procedure(proc_name, params=None):
    """Call a stored procedure and return notices."""
    conn = get_connection()
    conn.autocommit = True
    notices = []
    try:
        cur = conn.cursor()
        if params:
            cur.callproc(proc_name, params)
        else:
            cur.callproc(proc_name)
        notices = conn.notices[:]
        return notices
    except Exception as e:
        raise e
    finally:
        conn.close()


def call_function(func_name, params=None):
    """Call a stored function and return results + notices."""
    conn = get_connection()
    conn.autocommit = True
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        if params:
            cur.execute(f"SELECT * FROM {func_name}(%s)", params)
        else:
            cur.execute(f"SELECT * FROM {func_name}()")
        results = cur.fetchall()
        notices = conn.notices[:]
        return results, notices
    except Exception as e:
        raise e
    finally:
        conn.close()
