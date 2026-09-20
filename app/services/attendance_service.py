from collections import defaultdict
from app.models.attendance import DailyAttendance


class AttendanceService:

    def build_daily_attendance(self, df):
        grouped = defaultdict(list)

        for row in df.itertuples(index=False):
            key = (row.id, row.date)

            grouped[key].append(row.hour)

        result = []

        for (employee_id, work_date), punches in grouped.items():
            punches.sort()

            result.append(
                DailyAttendance(
                    employee_id=employee_id,
                    work_date=work_date,
                    punches=punches
                )
            )

        result.sort(
            key=lambda item: (
                item.employee_id,
                item.work_date
            )
        )

        return result