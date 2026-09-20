from dataclasses import dataclass
from datetime import timedelta


@dataclass
class EmployeeMonthlyReport:
    employee_id: str
    total_required_time: timedelta
    total_worked_time: timedelta
    total_overtime: timedelta
    total_shortage: timedelta
    total_delay: timedelta
    total_leave_time: timedelta
    total_allowed_leave_time: timedelta
    total_excess_leave_time: timedelta
    work_days: int
    absent_days: int
    incomplete_days: int
    multiple_punch_days: int
    holiday_days: int
    leave_days: int