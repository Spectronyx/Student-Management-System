import time
from typing import Optional, Dict, Any, List
from repositories.fee_repository import FeeRepository
from repositories.student_repository import StudentRepository
from utils.validators import validate_positive_number, validate_date, validate_required, ValidationError

class FeeService:
    """Service handling Fee structure assignment, Payment processing, and Balance calculations."""

    def __init__(self):
        self.fee_repo = FeeRepository()
        self.student_repo = StudentRepository()

    def assign_fee_record(self, student_id: int, semester: int, academic_year: str, total_amount: float, due_date_input: str) -> Dict[str, Any]:
        if not self.student_repo.get_by_id(student_id):
            raise ValidationError(f"Student ID {student_id} not found.")

        amount = validate_positive_number(total_amount, "Total Fee Amount")
        due_date = validate_date(due_date_input, "Due Date")
        year = validate_required(academic_year, "Academic Year")

        fee_id = self.fee_repo.create_fee_record(student_id, int(semester), year, amount, str(due_date))
        return self.fee_repo.get_fee_by_id(fee_id)

    def record_payment(self, fee_id: int, amount_paid_input: float, payment_method: str = "Online", transaction_ref: str = None) -> Dict[str, Any]:
        fee = self.fee_repo.get_fee_by_id(fee_id)
        if not fee:
            raise ValidationError(f"Fee record ID {fee_id} not found.")

        amount_paid = validate_positive_number(amount_paid_input, "Payment Amount")
        remaining_balance = float(fee['remaining_balance'])

        if amount_paid <= 0:
            raise ValidationError("Payment amount must be greater than zero.")

        if amount_paid > remaining_balance:
            raise ValidationError(f"Payment amount ({amount_paid}) exceeds remaining fee balance ({remaining_balance}).")

        if not transaction_ref:
            transaction_ref = f"TXN{int(time.time()*1000)}"

        method = validate_required(payment_method, "Payment Method")

        self.fee_repo.record_payment_transaction(fee_id, amount_paid, method, transaction_ref)
        return self.fee_repo.get_fee_by_id(fee_id)

    def get_student_fee_status(self, student_id: int) -> List[Dict[str, Any]]:
        return self.fee_repo.get_student_fees(student_id)

    def get_pending_fees_report(self) -> List[Dict[str, Any]]:
        return self.fee_repo.get_pending_fees()

    def get_paid_fees_report(self) -> List[Dict[str, Any]]:
        return self.fee_repo.get_paid_fees()

    def get_fee_summary(self) -> Dict[str, Any]:
        return self.fee_repo.get_fee_summary()
