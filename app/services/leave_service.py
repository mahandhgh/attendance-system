from collections import defaultdict
from datetime import date
from app.models.leave import Leave, LeaveType
from app.repositories.leave_repository import LeaveRepository
from app.utils.date_utils import jalali_year_month


class LeaveService:
    def __init__(self):
        self.repository = LeaveRepository()

    def add_leave(self, session, leave: Leave):
        if leave.duration_hours <= 0:
            raise ValueError(
                "Leave duration must be greater than zero."
            )

        valid_types = {
            LeaveType.ANNUAL,
            LeaveType.SICK,
            LeaveType.HOURLY,
        }

        if leave.leave_type not in valid_types:
            raise ValueError(
                f"Invalid leave type: {leave.leave_type}"
            )

        return self.repository.add(
            session=session,
            employee_code=leave.employee_code,
            leave_date=leave.leave_date,
            leave_type=leave.leave_type,
            duration_hours=leave.duration_hours,
            description=leave.description,
        )

    def get_month_leave_map(
        self,
        session,
        employee_code: str,
        start_date: date,
        end_date: date,
    ):
        rows = self.repository.get_for_employee_month(
            session=session,
            employee_code=employee_code,
            start_date=start_date,
            end_date=end_date,
        )

        leave_map = defaultdict(float)

        for row in rows:
            leave_date = self._normalize_date(row.leave_date)

            if row.leave_type == LeaveType.HOURLY:
                continue

            leave_map[row.leave_date] += float(
                row.duration_hours
            )

        return dict(leave_map)

    def get_month_leave_statistics(
        self,
        session,
        employee_code: str,
        start_date: date,
        end_date: date,
    ):
        rows = self.repository.get_for_employee_month(
            session=session,
            employee_code=employee_code,
            start_date=start_date,
            end_date=end_date,
        )

        statistics = {
            "annual_hours": 0.0,
            "sick_hours": 0.0,
            "hourly_hours": 0.0,
        }

        for row in rows:
            duration = float(row.duration_hours)

            if row.leave_type == LeaveType.ANNUAL:
                statistics["annual_hours"] += duration

            elif row.leave_type == LeaveType.SICK:
                statistics["sick_hours"] += duration

            elif row.leave_type == LeaveType.HOURLY:
                statistics["hourly_hours"] += duration

        return statistics

    def get_leave_statistics(self, session, employee_code, year_start, year_end):
        rows = self.repository.get_for_employee_month(
                    session=session,
                    employee_code=employee_code,
                    start_date=year_start,
                    end_date=year_end
                )

        monthly_statistics = defaultdict(
            lambda: {
                "annual_hours": 0.0,
                "sick_hours": 0.0,
                "hourly_hours": 0.0,
            }
        )

        for row in rows:
            leave_date = self._normalize_date(row.leave_date)

            year, month = jalali_year_month(leave_date)
            duration = float(row.duration_hours)

            if row.leave_type == LeaveType.ANNUAL:
                monthly_statistics[(year, month)]["annual_hours"] += duration

            elif row.leave_type == LeaveType.SICK:
                monthly_statistics[(year, month)]["sick_hours"] += duration

            elif row.leave_type == LeaveType.HOURLY:
                monthly_statistics[(year, month)]["hourly_hours"] += duration

        return dict(monthly_statistics)

    @staticmethod
    def _normalize_date(value):
        if isinstance(value, date):
            return value

        return date.fromisoformat(str(value))