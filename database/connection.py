import mysql.connector
import pymysql
import os
from contextlib import contextmanager
from config import config

class DatabaseManager:
    """Manages MySQL database connections, transactions, and schema execution."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def get_connection(self, use_db=True):
        """Creates and returns a new database connection."""
        conn_params = {
            'host': config.DB_HOST,
            'port': config.DB_PORT,
            'user': config.DB_USER,
            'password': config.DB_PASSWORD,
            'autocommit': False
        }
        if use_db:
            conn_params['database'] = config.DB_NAME

        try:
            if config.DB_SSL:
                conn_params['ssl_disabled'] = False
            connection = mysql.connector.connect(**conn_params)
            return connection
        except Exception as err:
            try:
                pymysql_params = {
                    'host': config.DB_HOST,
                    'port': config.DB_PORT,
                    'user': config.DB_USER,
                    'password': config.DB_PASSWORD,
                    'autocommit': False
                }
                if use_db:
                    pymysql_params['database'] = config.DB_NAME
                if config.DB_SSL:
                    pymysql_params['ssl'] = {'ssl_mode': 'REQUIRED'}
                return pymysql.connect(**pymysql_params)
            except Exception as py_err:
                raise Exception(f"Database Connection Error: {err} | PyMySQL Error: {py_err}")

    @contextmanager
    def transaction(self):
        """Context manager for executing database operations in a single transaction."""
        conn = self.get_connection(use_db=True)
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

    def initialize_schema(self, schema_path=None):
        """Executes the SQL schema script to setup tables and initial demo data."""
        if schema_path is None:
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

        conn = self.get_connection(use_db=True)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            lines = [l for l in sql_content.splitlines() if not (l.strip().upper().startswith("CREATE DATABASE") or l.strip().upper().startswith("USE "))]
            clean_sql = "\n".join(lines)

            raw_stmts = clean_sql.split(';')
            for stmt in raw_stmts:
                lines_s = [line for line in stmt.splitlines() if not line.strip().startswith('--') and not line.strip().startswith('/*')]
                s = "\n".join(lines_s).strip()
                if s:
                    cursor.execute(s)

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            return True
        except Exception as err:
            conn.rollback()
            raise Exception(f"Failed to initialize database schema: {err}")
        finally:
            cursor.close()
            conn.close()

db_manager = DatabaseManager()

def get_connection(use_db=True):
    return db_manager.get_connection(use_db=use_db)
