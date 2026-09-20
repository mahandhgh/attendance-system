from dataclasses import dataclass


@dataclass(frozen=True)
class LeavePolicy:
    annual_leave_days_per_year: float = 26.0
    sick_leave_days_per_year: float | None = None

    standard_daily_hours: float = 8.0

DEFAULT_LEAVE_POLICY = LeavePolicy()