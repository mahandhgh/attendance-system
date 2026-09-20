from datetime import date
from sqlalchemy import text


class LeaveRepository:
    def add(
        self,
        session,
        employee_code: str,
        leave_date: date,
        leave_type: str,
        duration_hours: float,
        description: str | None = None,
    ):
        result = session.execute(
            text(
                """
                INSERT INTO leaves
                (
                    employee_code,
                    leave_date,
                    leave_type,
                    duration_hours,
                    description
                )
                VALUES
                (
                    :employee_code,
                    :leave_date,
                    :leave_type,
                    :duration_hours,
                    :description
                )
                """
            ),
            {
                "employee_code": employee_code,
                "leave_date": leave_date.isoformat(),
                "leave_type": leave_type,
                "duration_hours": duration_hours,
                "description": description,
            },
        )

        session.commit()

        return result

    def get_for_employee_month(
        self,
        session,
        employee_code: str,
        start_date: date,
        end_date: date,
    ):
        result = session.execute(
            text(
                """
                SELECT
                    employee_code,
                    leave_date,
                    leave_type,
                    duration_hours,
                    description
                FROM leaves
                WHERE employee_code = :employee_code
                  AND leave_date BETWEEN :start_date AND :end_date
                ORDER BY leave_date
                """
            ),
            {
                "employee_code": employee_code,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )

        return result.fetchall()