from decimal import Decimal

from app.repositories.salary_rate_repository import SalaryRateRepository


class SalaryRateService:
    def __init__(self):
        self.repository = SalaryRateRepository()

    def save_rate(self, session, employee_code, hourly_rate):
        hourly_rate = Decimal(str(hourly_rate))

        if hourly_rate < 0:
            raise ValueError(
                "Hourly rate cannot be negative."
            )

        return self.repository.set_rate(
            session=session,
            employee_code=employee_code,
            hourly_rate=hourly_rate,
        )

    def get_rate(self, session, employee_code):
        return self.repository.get(
            session=session,
            employee_code=employee_code,
        )

    def get_all_rates(self, session):
        return self.repository.get_all(session=session)