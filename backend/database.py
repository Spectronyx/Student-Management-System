import pymysql
import mysql.connector
import os
from contextlib import contextmanager
from config import settings

def get_db_connection():
    """Creates a new database connection with SSL and dictionary cursor support."""
    params = {
        'host': settings.DB_HOST,
        'port': settings.DB_PORT,
        'user': settings.DB_USER,
        'password': settings.DB_PASSWORD,
        'database': settings.DB_NAME,
        'autocommit': False
    }

    try:
        if settings.DB_SSL:
            params['ssl_disabled'] = False
        conn = mysql.connector.connect(**params)
        return conn
    except Exception as err:
        try:
            py_params = {
                'host': settings.DB_HOST,
                'port': settings.DB_PORT,
                'user': settings.DB_USER,
                'password': settings.DB_PASSWORD,
                'database': settings.DB_NAME,
                'autocommit': False,
                'cursorclass': pymysql.cursors.DictCursor
            }
            if settings.DB_SSL:
                py_params['ssl'] = {'ssl_mode': 'REQUIRED'}
            return pymysql.connect(**py_params)
        except Exception as py_err:
            raise RuntimeError(f"Database Connection Failed: {err} | PyMySQL Error: {py_err}")

@contextmanager
def get_db():
    """Context manager for executing database operations with auto commit/rollback."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) if hasattr(conn, 'cursor') and not hasattr(conn, 'DictCursor') else conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def fetch_all(query: str, params: tuple = ()):
    with get_db() as cursor:
        cursor.execute(query, params)
        res = cursor.fetchall()
        if res and isinstance(res[0], tuple) and hasattr(cursor, 'description'):
            colnames = [desc[0] for desc in cursor.description]
            return [dict(zip(colnames, row)) for row in res]
        return res or []

def fetch_one(query: str, params: tuple = ()):
    with get_db() as cursor:
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row and isinstance(row, tuple) and hasattr(cursor, 'description'):
            colnames = [desc[0] for desc in cursor.description]
            return dict(zip(colnames, row))
        return row

def execute_query(query: str, params: tuple = ()) -> int:
    with get_db() as cursor:
        cursor.execute(query, params)
        return cursor.lastrowid or cursor.rowcount

def init_db():
    """Executes schema.sql and seed.sql scripts on server initialization."""
    base_dir = os.path.dirname(__file__)
    schema_path = os.path.join(base_dir, 'schema.sql')
    seed_path = os.path.join(base_dir, 'seed.sql')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # Execute Schema
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            for stmt in schema_sql.split(';'):
                lines = [l for l in stmt.splitlines() if not l.strip().startswith('--') and not l.strip().startswith('/*')]
                clean_stmt = "\n".join(lines).strip()
                if clean_stmt:
                    cursor.execute(clean_stmt)

        # Execute Seed Data
        if os.path.exists(seed_path):
            with open(seed_path, 'r', encoding='utf-8') as f:
                seed_sql = f.read()
            for stmt in seed_sql.split(';'):
                lines = [l for l in stmt.splitlines() if not l.strip().startswith('--') and not l.strip().startswith('/*')]
                clean_stmt = "\n".join(lines).strip()
                if clean_stmt:
                    cursor.execute(clean_stmt)

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print("Database schema and seed data initialized successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Warning initializing database schema: {e}")
    finally:
        cursor.close()
        conn.close()
