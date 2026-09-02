from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date, datetime

@dataclass
class Fee:
    fee_id: Optional[int]
    student_id: int
    semester: int
    academic_year: str
    total_amount: float
    due_date: date
    status: str  # 'Pending', 'Partial', 'Paid'
    student_name: Optional[str] = None
    paid_amount: float = 0.0

    @property
    def remaining_balance(self) -> float:
        return max(0.0, self.total_amount - self.paid_amount)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fee_id": self.fee_id,
            "student_id": self.student_id,
            "semester": self.semester,
            "academic_year": self.academic_year,
            "total_amount": self.total_amount,
            "paid_amount": self.paid_amount,
            "remaining_balance": self.remaining_balance,
            "due_date": str(self.due_date),
            "status": self.status,
            "student_name": self.student_name
        }

@dataclass
class Payment:
    payment_id: Optional[int]
    fee_id: int
    amount_paid: float
    payment_date: datetime
    payment_method: str
    transaction_ref: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "payment_id": self.payment_id,
            "fee_id": self.fee_id,
            "amount_paid": self.amount_paid,
            "payment_date": self.payment_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.payment_date, datetime) else str(self.payment_date),
            "payment_method": self.payment_method,
            "transaction_ref": self.transaction_ref
        }
