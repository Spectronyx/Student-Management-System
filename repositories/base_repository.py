from typing import List, Dict, Any, Optional
from database.connection import get_connection

class BaseRepository:
    """Base repository with parameterized SQL query execution utilities."""

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as dictionaries."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True) if hasattr(conn, 'cursor') and not hasattr(conn, 'DictCursor') else conn.cursor()
        try:
            cursor.execute(query, params)
            if hasattr(cursor, 'fetchall'):
                results = cursor.fetchall()
                # Handle PyMySQL dictionary cursor tuple formatting if needed
                if results and isinstance(results[0], tuple) and hasattr(cursor, 'description'):
                    colnames = [desc[0] for desc in cursor.description]
                    return [dict(zip(colnames, row)) for row in results]
                return results or []
            return []
        finally:
            cursor.close()
            conn.close()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Executes SELECT query and returns single row or None."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True) if hasattr(conn, 'cursor') and not hasattr(conn, 'DictCursor') else conn.cursor()
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row and isinstance(row, tuple) and hasattr(cursor, 'description'):
                colnames = [desc[0] for desc in cursor.description]
                return dict(zip(colnames, row))
            return row
        finally:
            cursor.close()
            conn.close()

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Executes INSERT query and returns inserted primary key ID."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            last_id = cursor.lastrowid
            return last_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def execute_update_delete(self, query: str, params: tuple = ()) -> int:
        """Executes UPDATE or DELETE query and returns affected rows count."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            affected = cursor.rowcount
            return affected
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
