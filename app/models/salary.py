from dataclasses import dataclass
from decimal import Decimal


@dataclass
class SalaryCalculation:
    employee_id: str
    hourly_rate: Decimal
    overtime_hours: Decimal
    overtime_pay: Decimal
    shortage_hours: Decimal
    shortage_deduction: Decimal
    excess_leave_hours: Decimal
    excess_leave_deduction: Decimal
    total_deduction: Decimal
    net_adjustment: Decimal