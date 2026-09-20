from sqlalchemy import Column, Integer, String, UniqueConstraint
from app.database.base import Base
from app.models import employee_log

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(
        Integer,
        primary_key=True
    )

    employee_id = Column(
        String,
        nullable=False
    )

    work_date = Column(
        String,
        nullable=False
    )

    punch_time = Column(
        String,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "work_date",
            "punch_time",
            name="uq_attendance_log"
        ),
    )