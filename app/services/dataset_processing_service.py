from collections import defaultdict
from app.database.connection import SessionLocal
from app.services.attendance_service import AttendanceService
from app.services.calendar_service import CalendarService
from app.services.attendance_calendar_merger import AttendanceCalendarMerger
from app.services.work_time_service import WorkTimeService
from app.services.monthly_report_service import MonthlyReportService
from app.services.leave_service import LeaveService
from app.services.leave_policy_service import LeavePolicyService
from app.config.leave_policy import DEFAULT_LEAVE_POLICY
from app.utils.date_utils import jalali_year_month, jalali_year_start_end


class DatasetProcessingService:
    def __init__(self):
        self.attendance_service = AttendanceService()
        self.calendar_service = CalendarService()
        self.merger = AttendanceCalendarMerger()
        self.work_time_service = WorkTimeService()
        self.monthly_report_service = MonthlyReportService()
        self.leave_service = LeaveService()
        self.leave_policy_service = LeavePolicyService(policy=DEFAULT_LEAVE_POLICY)

    def process(self, df):
        month_groups = defaultdict(list)

        for row in df.itertuples(index=False):
            year, month = jalali_year_month(row.date)
            month_groups[(year, month)].append(row)

        monthly_data = []
        session = SessionLocal()

        try:

            for (year, month), rows in sorted(month_groups.items()):
                month_df = df[df["date"].apply(jalali_year_month).apply(lambda x: x == (year, month))]

                calendar_days = (
                    self.calendar_service.get_month_days(
                        year,
                        month
                    )
                )

                daily_attendance = (
                    self.attendance_service.build_daily_attendance(month_df)
                )

                employee_ids = sorted(
                    month_df["id"].unique()
                )

                month_start = calendar_days[0].date
                month_end = calendar_days[-1].date

                for employee_id in employee_ids:
                    merged_days = (
                        self.merger.merge_employee_month(
                            employee_id=employee_id,
                            calendar_days=calendar_days,
                            daily_attendance=daily_attendance
                        )
                    )

                    leave_map = (
                        self.leave_service.get_month_leave_map(
                            session=session,
                            employee_code=employee_id,
                            start_date=month_start,
                            end_date=month_end,
                        )
                    )

                    daily_summaries = []

                    for attendance, calendar_day in merged_days:
                        leave_hours = leave_map.get(calendar_day.date, 0.0)

                        summary = (
                            self.work_time_service.calculate(
                                attendance,
                                calendar_day,
                                leave_hours
                            )
                        )

                        daily_summaries.append(summary)

                    leave_statistics = self.leave_service.get_month_leave_statistics(
                                                            session=session,
                                                            employee_code=employee_id,
                                                            start_date=month_start,
                                                            end_date=month_end
                                                        )

                    monthly_data.append({
                        "year": year,
                        "month": month,
                        "employee_id": employee_id,
                        "daily_summary": daily_summaries,
                        "leave_statistics": leave_statistics
                    })

        finally:
            session.close()

        annual_leave_data = defaultdict(dict)

        for item in monthly_data:
            key = (item["employee_id"], item["year"])

            annual_leave_data[key][(item["year"], item["month"])] = item["leave_statistics"]

        annual_excess_by_employee_year = {}

        for (employee_id, year), monthly_statistics in (annual_leave_data.items()):
            year_start, year_end = jalali_year_start_end(year)

            excess_by_month = (
                self.leave_policy_service
                .calculate_annual_excess_by_month(
                    monthly_statistics
                )
            )

            annual_excess_by_employee_year[(employee_id, year)] = excess_by_month

        all_reports = []

        for item in monthly_data:
            year = item["year"]
            month = item["month"]
            employee_id = item["employee_id"]

            excess_map = (
                annual_excess_by_employee_year.get(
                    (employee_id, year), {}
                )
            )

            excess_statistics = (
                excess_map.get(
                    (year, month), {}
                )
            )

            excess_leave_hours = (
                excess_statistics.get(
                    "total_excess_hours", 0.0
                )
            )

            report = (
                self.monthly_report_service
                .create_employee_report(
                    employee_id=employee_id,
                    daily_summaries=(item["daily_summary"]),
                    excess_leave_hours=excess_leave_hours
                )
            )

            all_reports.append(
                (
                    year,
                    month,
                    report,
                )
            )

        return all_reports