from app.database.connection import SessionLocal
from app.models.employee_log import Employee


session = SessionLocal()


employee = Employee(
    employee_code="0000000001"
)


session.add(employee)

session.commit()


print("Saved")


session.close()