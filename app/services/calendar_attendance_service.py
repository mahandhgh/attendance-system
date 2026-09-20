from datetime import date


class CalendarAttendanceService:
    def match_calendar_with_attendance(self, daily_attendance, calendar_days):
        calendar_map = {day.date: day for day in calendar_days}
        matched = []

        for attendance in daily_attendance:
            calendar_day = calendar_map.get(attendance.work_date)

            if calendar_day is None:
                continue
            matched.append((attendance, calendar_day))

        return matched