from app.database.connection import engine
from sqlalchemy import text
from app.database.base import Base
from app.database.database import Database
from app.models.employee_log import EmployeeLog
from app.models.attendance_log import AttendanceLog
from app.models.salary_rate import SalaryRate


def init_database():
    Base.metadata.create_all(bind=engine)
    db = Database()
    db.create_tables()

    with engine.begin() as connection:
        connection.execute(
            text("""
                CREATE UNIQUE INDEX IF NOT EXISTS
                uq_attendance_log_unique
                ON attendance_logs (
                    employee_id,
                    work_date,
                    punch_time
                )
            """)
        )

    print("Database initialized successfully.")

if __name__ == "__main__":
    init_database()
