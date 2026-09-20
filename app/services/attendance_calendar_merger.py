from app.models.attendance import DailyAttendance

class AttendanceCalendarMerger:
    def merge_employee_month(self, employee_id, calendar_days, daily_attendance):
        attendance_map = {
            item.work_date: item
            for item in daily_attendance
            if item.employee_id == employee_id
        }
        result = []
        for day in calendar_days:
            attendance = attendance_map.get(day.date)
            if attendance is not None:
                result.append((attendance, day))
            else:
                result.append((
                        DailyAttendance(
                            employee_id=employee_id,
                            work_date=day.date,
                            punches=[]
                        ),
                        day
                    ))

        return result