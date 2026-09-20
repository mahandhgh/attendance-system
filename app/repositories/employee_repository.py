from app.models.employee_log import EmployeeLog


class EmployeeRepository:
    def get_or_create(self, session, employee_code):
        employee = (
            session.query(EmployeeLog).filter_by(employee_code=employee_code).first()
        )
        if employee:
            return employee

        employee = EmployeeLog(
            employee_code=employee_code
        )

        session.add(employee)
        session.commit()
        
        return employee