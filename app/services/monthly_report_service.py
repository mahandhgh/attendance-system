from bdb import effective
from datetime import timedelta

from app.models.monthly_report import EmployeeMonthlyReport


class MonthlyReportService:

    def create_employee_report(self, employee_id, daily_summaries, excess_leave_hours=0.0):
        employee_summaries = [
            item
            for item in daily_summaries
            if item.employee_id == employee_id
        ]

        total_required = sum((item.required_time for item in employee_summaries), timedelta())

        total_worked = sum((item.worked_time for item in employee_summaries), timedelta())

        total_delay = sum((item.delay for item in employee_summaries), timedelta())

        total_leave = sum((item.leave_time for item in employee_summaries), timedelta())

        excess_leave_time = timedelta(hours=excess_leave_hours)

        if excess_leave_time > total_leave:
            excess_leave_time = total_leave
        
        allowed_leave_time = total_leave - excess_leave_time

        if allowed_leave_time < timedelta(0):
            allowed_leave_time = timedelta(0)

        effective_required = total_required - allowed_leave_time

        if effective_required < timedelta(0):
            effective_required = timedelta(0)

        net_balance = total_worked - effective_required

        if net_balance > timedelta(0):
            total_overtime = net_balance
            total_shortage = timedelta(0)

        elif net_balance < timedelta(0):
            total_overtime = timedelta(0)
            total_shortage = abs(net_balance)

        else:
            total_overtime = timedelta(0)
            total_shortage = timedelta(0)

        absent_days = sum(item.status == "absent" for item in employee_summaries)

        incomplete_days = sum(item.status == "incomplete" for item in employee_summaries)

        multiple_punch_days = sum(item.status == "multiple_punches" for item in employee_summaries)

        holiday_days = sum(item.status == "holiday" for item in employee_summaries)

        leave_days = sum(item.status == "leave" for item in employee_summaries)

        work_days = sum(item.status == "complete" for item in employee_summaries)

        return EmployeeMonthlyReport(
            employee_id=employee_id,
            total_required_time=total_required,
            total_worked_time=total_worked,
            total_overtime=total_overtime,
            total_shortage=total_shortage,
            total_delay=total_delay,
            total_leave_time=total_leave,
            total_excess_leave_time=excess_leave_time,
            total_allowed_leave_time=allowed_leave_time,
            work_days=work_days,
            absent_days=absent_days,
            incomplete_days=incomplete_days,
            multiple_punch_days=multiple_punch_days,
            holiday_days=holiday_days,
            leave_days=leave_days,
        )