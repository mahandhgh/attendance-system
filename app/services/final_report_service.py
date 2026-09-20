from decimal import Decimal
from app.models.final_report import MonthlyFinalReport
from app.services.salary_service import SalaryService


class FinalReportService:
    def __init__(self, salary_service=None):
        self.salary_service = (
            salary_service
            if salary_service is not None
            else SalaryService()
        )

    def build(self, monthly_reports, hourly_rates=None, default_hourly_rate=Decimal("0")):
        if hourly_rates is None:
            hourly_rates = {}

        results = []

        for year, month, report in monthly_reports:

            hourly_rate = hourly_rates.get(
                report.employee_id,
                default_hourly_rate,
            )

            salary = self.salary_service.calculate(
                report=report,
                hourly_rate=hourly_rate,
            )

            results.append(
                MonthlyFinalReport(
                    year=year,
                    month=month,
                    attendance_report=report,
                    salary_calculation=salary,
                )
            )

        return results