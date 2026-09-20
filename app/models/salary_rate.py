from sqlalchemy import Column, Integer, String, Numeric, UniqueConstraint
from app.database.base import Base


class SalaryRate(Base):
    __tablename__ = "salary_rates"

    id = Column(Integer, primary_key=True)

    employee_code = Column(
        String,
        nullable=False,
    )

    hourly_rate = Column(
        Numeric(18, 2),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "employee_code",
            name="uq_salary_rate_employee",
        ),
    )