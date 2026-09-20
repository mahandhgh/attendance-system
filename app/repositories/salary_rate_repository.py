from decimal import Decimal
from app.models.salary_rate import SalaryRate


class SalaryRateRepository:
    def get(self, session, employee_code):
        record = (
            session.query(SalaryRate)
            .filter_by(employee_code=employee_code)
            .first()
        )

        if record is None:
            return None

        return Decimal(str(record.hourly_rate))

    def set_rate(self, session, employee_code, hourly_rate):
        record = (
            session.query(SalaryRate)
            .filter_by(employee_code=employee_code)
            .first()
        )

        if record is None:
            record = SalaryRate(
                employee_code=employee_code,
                hourly_rate=hourly_rate,
            )

            session.add(record)

        else:
            record.hourly_rate = hourly_rate

        session.commit()

        return record

    def get_all(self, session):
        records = (
            session.query(SalaryRate)
            .all()
        )

        return {
            record.employee_code: Decimal(
                str(record.hourly_rate)
            )
            for record in records
        }