from dataclasses import dataclass
from app.models.monthly_report import EmployeeMonthlyReport
from app.models.salary import SalaryCalculation


@dataclass
class MonthlyFinalReport:
    year: int
    month: int
    attendance_report: EmployeeMonthlyReport
    salary_calculation: SalaryCalculation