from dataclasses import dataclass

@dataclass(frozen=True)
class SalaryPolicy:
    overtime_multiplier = 1.0
    shortage_multiplier = 1.0
    excess_leave_multiplier = 1.0

DEFAULT_SALARY_POLICY = SalaryPolicy()