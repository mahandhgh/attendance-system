from datetime import timedelta
from app.models.work_summary import DailyWorkSummary


class WorkTimeService:
    def calculate(self, attendance, calendar_day, leave_hours=0):
        required_time = timedelta(hours=calendar_day.required_hours)
        leave_time = timedelta(hours=leave_hours)

        # Holiday / Friday
        if calendar_day.required_hours == 0:
            return DailyWorkSummary(
                employee_id=attendance.employee_id,
                work_date=attendance.work_date,
                required_time=timedelta(0),
                worked_time=timedelta(0),
                check_in=None,
                check_out=None,
                overtime=timedelta(0),
                shortage=timedelta(0),
                delay=timedelta(0),
                status="holiday",
                leave_time=timedelta(0)
            )
        
        effective_required_time = (required_time - leave_time)

        if effective_required_time < timedelta(0):
            effective_required_time = timedelta(0)

        punches = attendance.punches

        # No attendance
        if len(punches) == 0:
            shortage = effective_required_time

            status = ("leave" if leave_time > timedelta(0) else "absent")

            return DailyWorkSummary(
                employee_id=attendance.employee_id,
                work_date=attendance.work_date,
                required_time=required_time,
                worked_time=timedelta(0),
                check_in=None,
                check_out=None,
                overtime=timedelta(0),
                shortage=shortage,
                delay=timedelta(0),
                status=status,
                leave_time=leave_time
            )

        # Incomplete attendance
        if len(punches) == 1:
            status = ("leave" if leave_time > timedelta(0) else "incomplete")
            
            return DailyWorkSummary(
                employee_id=attendance.employee_id,
                work_date=attendance.work_date,
                required_time=required_time,
                worked_time=timedelta(0),
                check_in=None,
                check_out=None,
                overtime=timedelta(0),
                shortage=effective_required_time,
                delay=timedelta(0),
                status=status,
                leave_time=leave_time
            )

        worked_time = self.calculate_worked_time(punches)

        first_check_in = punches[0]
        last_check_out = punches[-1]

        normalized_check_in = self.normalize_check_in(first_check_in)

        delay = self.calculate_delay(first_check_in)

        difference = worked_time - effective_required_time

        if difference > timedelta(0):
            overtime = difference
            shortage = timedelta(0)
        else:
            overtime = timedelta(0)
            shortage = abs(difference)

        status = "complete"

        if len(punches) > 2:
            status = "multiple_punches"

        return DailyWorkSummary(
            employee_id=attendance.employee_id,
            work_date=attendance.work_date,
            required_time=required_time,
            worked_time=worked_time,
            check_in=normalized_check_in,
            check_out=last_check_out,
            overtime=overtime,
            shortage=shortage,
            delay=delay,
            status=status,
            leave_time=leave_time,
        )

    def calculate_worked_time(self, punches):
        total_worked = timedelta(0)

        for index in range(0, len(punches) - 1, 2):
            check_in = punches[index]
            check_out = punches[index + 1]

            effective_check_in = self.normalize_check_in(check_in)

            if check_out > effective_check_in:
                total_worked += (check_out - effective_check_in)

        return total_worked

    def normalize_check_in(self, check_in):
        start_time = timedelta(hours=9)
        allowed_time = timedelta(hours=9, minutes=15)

        if start_time <= check_in <= allowed_time:
            return start_time

        return check_in

    def calculate_delay(self, check_in):
        start_time = timedelta(hours=9)
        allowed_time = timedelta(hours=9, minutes=15)

        if check_in <= allowed_time:
            return timedelta(0)

        return check_in - start_time