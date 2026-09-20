from dataclasses import dataclass
from datetime import date


class LeaveType:
    ANNUAL = "annual"
    SICK = "sick"
    HOURLY = "hourly"

@dataclass
class Leave:
    employee_code: str
    leave_date: date
    leave_type: str
    duration_hours: float
    description: str | None = None