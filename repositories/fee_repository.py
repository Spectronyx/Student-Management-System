from typing import Optional, Dict, Any, List
from repositories.base_repository import BaseRepository
from database.connection import db_manager

class FeeRepository(BaseRepository):
    """Repository for Fees and Payments SQL database operations."""

    def create_fee_record(self, student_id: int, semester: int, academic_year: str, total_amount: float, due_date: str) -> int:
        query = """
            INSERT INTO fees (student_id, semester, academic_year, total_amount, due_date, status)
            VALUES (%s, %s, %s, %s, %s, 'Pending')
        """
        return self.execute_insert(query, (student_id, semester, academic_year, total_amount, due_date))

    def get_fee_by_id(self, fee_id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT f.*, CONCAT(s.first_name, ' ', s.last_name) AS student_name, s.roll_number,
                   COALESCE(SUM(p.amount_paid), 0.00) AS paid_amount,
                   (f.total_amount - COALESCE(SUM(p.amount_paid), 0.00)) AS remaining_balance
            FROM fees f
            JOIN students s ON f.student_id = s.student_id
            LEFT JOIN payments p ON f.fee_id = p.fee_id
            WHERE f.fee_id = %s
            GROUP BY f.fee_id, s.first_name, s.last_name, s.roll_number
        """
        return self.fetch_one(query, (fee_id,))

    def get_student_fees(self, student_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT f.*, 
                   COALESCE(SUM(p.amount_paid), 0.00) AS paid_amount,
                   (f.total_amount - COALESCE(SUM(p.amount_paid), 0.00)) AS remaining_balance
            FROM fees f
            LEFT JOIN payments p ON f.fee_id = p.fee_id
            WHERE f.student_id = %s
            GROUP BY f.fee_id
            ORDER BY f.due_date DESC
        """
        return self.execute_query(query, (student_id,))

    def record_payment_transaction(self, fee_id: int, amount_paid: float, payment_method: str, transaction_ref: str) -> bool:
        """Executes payment insertion and updates fee status atomically inside a transaction."""
        with db_manager.transaction() as cursor:
            # 1. Insert Payment Record
            insert_payment_sql = """
                INSERT INTO payments (fee_id, amount_paid, payment_method, transaction_ref)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_payment_sql, (fee_id, amount_paid, payment_method, transaction_ref))

            # 2. Recalculate Total Paid & Update Fee Status
            calc_sql = """
                SELECT f.total_amount, COALESCE(SUM(p.amount_paid), 0.00) AS total_paid
                FROM fees f
                LEFT JOIN payments p ON f.fee_id = p.fee_id
                WHERE f.fee_id = %s
                GROUP BY f.fee_id
            """
            cursor.execute(calc_sql, (fee_id,))
            fee_info = cursor.fetchone()
            
            # Normalize dictionary row
            if isinstance(fee_info, tuple) and hasattr(cursor, 'description'):
                colnames = [desc[0] for desc in cursor.description]
                fee_info = dict(zip(colnames, fee_info))

            if fee_info:
                total_amount = float(fee_info['total_amount'])
                total_paid = float(fee_info['total_paid'])

                if total_paid >= total_amount:
                    new_status = 'Paid'
                elif total_paid > 0:
                    new_status = 'Partial'
                else:
                    new_status = 'Pending'

                update_status_sql = "UPDATE fees SET status = %s WHERE fee_id = %s"
                cursor.execute(update_status_sql, (new_status, fee_id))

        return True

    def get_pending_fees(self) -> List[Dict[str, Any]]:
        query = """
            SELECT f.fee_id, s.roll_number, CONCAT(s.first_name, ' ', s.last_name) AS student_name,
                   c.course_name, f.semester, f.academic_year, f.total_amount,
                   COALESCE(SUM(p.amount_paid), 0.00) AS paid_amount,
                   (f.total_amount - COALESCE(SUM(p.amount_paid), 0.00)) AS remaining_balance,
                   f.due_date, f.status
            FROM fees f
            JOIN students s ON f.student_id = s.student_id
            JOIN courses c ON s.course_id = c.course_id
            LEFT JOIN payments p ON f.fee_id = p.fee_id
            GROUP BY f.fee_id, s.roll_number, student_name, c.course_name
            HAVING f.status IN ('Pending', 'Partial') OR remaining_balance > 0
            ORDER BY f.due_date ASC
        """
        return self.execute_query(query)

    def get_paid_fees(self) -> List[Dict[str, Any]]:
        query = """
            SELECT f.fee_id, s.roll_number, CONCAT(s.first_name, ' ', s.last_name) AS student_name,
                   c.course_name, f.semester, f.academic_year, f.total_amount,
                   f.due_date, f.status
            FROM fees f
            JOIN students s ON f.student_id = s.student_id
            JOIN courses c ON s.course_id = c.course_id
            WHERE f.status = 'Paid'
            ORDER BY f.fee_id DESC
        """
        return self.execute_query(query)

    def get_fee_summary(self) -> Dict[str, Any]:
        query = """
            SELECT 
                COUNT(DISTINCT f.fee_id) AS total_fee_records,
                COALESCE(SUM(f.total_amount), 0.00) AS total_receivable,
                COALESCE(SUM(p.amount_paid), 0.00) AS total_collected,
                (COALESCE(SUM(f.total_amount), 0.00) - COALESCE(SUM(p.amount_paid), 0.00)) AS total_pending
            FROM fees f
            LEFT JOIN payments p ON f.fee_id = p.fee_id
        """
        return self.fetch_one(query) or {}
