from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class DailyWorkSummary:
    employee_id: str
    work_date: date
    required_time: timedelta
    worked_time: timedelta
    check_in: timedelta | None
    check_out: timedelta | None
    overtime: timedelta
    shortage: timedelta
    delay: timedelta
    status: str
    leave_time: timedelta = timedelta(0)