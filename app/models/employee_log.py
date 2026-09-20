from sqlalchemy import Column, Integer, String, Boolean
from app.database.base import Base


class EmployeeLog(Base):
    __tablename__ = "employees"

    id = Column(
        Integer,
        primary_key=True
    )

    employee_code = Column(
        String,
        unique=True,
        nullable=False
    )

    name = Column(
        String,
        nullable=True
    )

    family = Column(
        String,
        nullable=True
    )

    active = Column(
        Boolean,
        default=True
    )