from decimal import Decimal
from pathlib import Path

from app.database.init_db import init_database
from app.database.connection import SessionLocal

from app.readers.attendance_reader import AttendanceReader
from app.services.database_import_service import (
    DatabaseImportService,
)
from app.services.dataset_processing_service import (
    DatasetProcessingService,
)
from app.services.final_report_service import (
    FinalReportService,
)
from app.services.salary_service import SalaryService
from app.services.salary_rate_service import SalaryRateService
from app.config.salary_policy import DEFAULT_SALARY_POLICY

from app.utils.time_utils import format_timedelta

DEFAULT_HOURLY_RATE = Decimal("100000")


def main():

    print("=" * 80)
    print("ATTENDANCE SYSTEM")
    print("=" * 80)

    # -------------------------------------------------
    # 1. Initialize database
    # -------------------------------------------------

    print("\n[1] Initializing database...")

    init_database()

    print("Database initialized successfully.")

    # -------------------------------------------------
    # 2. Read attendance file
    # -------------------------------------------------

    file_path = Path("data/HR.TXT")

    print("\n[2] Reading attendance file...")

    reader = AttendanceReader()

    df = reader.read(file_path)

    print(f"Total records: {len(df)}")
    print(f"Employees: {df['id'].nunique()}")

    # -------------------------------------------------
    # 3. Import attendance data
    # -------------------------------------------------

    print("\n[3] Importing attendance data...")

    salary_rate_service = SalaryRateService()

    session = SessionLocal()

    try:
        hourly_rates = (
            salary_rate_service.get_all_rates(
                session=session
            )
        )

    finally:
        session.close()

    # -------------------------------------------------
    # 4. Process dataset
    # -------------------------------------------------

    print("\n[4] Processing dataset...")

    processor = DatasetProcessingService()

    monthly_reports = processor.process(df)

    print(
        f"Monthly reports generated: "
        f"{len(monthly_reports)}"
    )

    # -------------------------------------------------
    # 5. Build final reports
    # -------------------------------------------------

    print("\n[5] Calculating salary reports...")

    salary_service = SalaryService(
        policy=DEFAULT_SALARY_POLICY
    )

    final_report_service = FinalReportService(
        salary_service=salary_service
    )

    final_reports = final_report_service.build(
        monthly_reports=monthly_reports,
        hourly_rates=hourly_rates,
        default_hourly_rate=Decimal("0"),
    )

    # -------------------------------------------------
    # 6. Display final reports
    # -------------------------------------------------

    print("\n" + "=" * 100)
    print("FINAL MONTHLY REPORTS")
    print("=" * 100)

    for result in final_reports:

        report = result.attendance_report
        salary = result.salary_calculation

        print("\n" + "-" * 100)

        print(
            f"Employee ID: {report.employee_id}"
        )

        print(
            f"Jalali Month: "
            f"{result.year}/{result.month:02d}"
        )

        print("\n--- Attendance ---")

        print(
            f"Required time: "
            f"{format_timedelta(report.total_required_time)}"
        )

        print(
            f"Worked time:   "
            f"{format_timedelta(report.total_worked_time)}"
        )

        print(
            f"Overtime:      "
            f"{format_timedelta(report.total_overtime)}"
        )

        print(
            f"Shortage:      "
            f"{format_timedelta(report.total_shortage)}"
        )

        print(
            f"Delay:         "
            f"{format_timedelta(report.total_delay)}"
        )

        print(
            f"Leave time:    "
            f"{format_timedelta(report.total_leave_time)}"
        )

        print(
            f"Allowed leave: "
            f"{format_timedelta(report.total_allowed_leave_time)}"
        )

        print(
            f"Excess leave:  "
            f"{format_timedelta(report.total_excess_leave_time)}"
        )

        print("\n--- Day Statistics ---")

        print(
            f"Work days:           {report.work_days}"
        )

        print(
            f"Absent days:         {report.absent_days}"
        )

        print(
            f"Incomplete days:     {report.incomplete_days}"
        )

        print(
            f"Multiple punch days: "
            f"{report.multiple_punch_days}"
        )

        print(
            f"Holiday days:        {report.holiday_days}"
        )

        print(
            f"Leave days:          {report.leave_days}"
        )

        print("\n--- Salary ---")

        print(
            f"Hourly rate: "
            f"{salary.hourly_rate}"
        )

        print(
            f"Overtime hours: "
            f"{salary.overtime_hours}"
        )

        print(
            f"Overtime pay: "
            f"{salary.overtime_pay}"
        )

        print(
            f"Shortage hours: "
            f"{salary.shortage_hours}"
        )

        print(
            f"Shortage deduction: "
            f"{salary.shortage_deduction}"
        )

        print(
            f"Excess leave hours: "
            f"{salary.excess_leave_hours}"
        )

        print(
            f"Excess leave deduction: "
            f"{salary.excess_leave_deduction}"
        )

        print(
            f"Total deduction: "
            f"{salary.total_deduction}"
        )

        print(
            f"Net adjustment: "
            f"{salary.net_adjustment}"
        )

    print("\n" + "=" * 80)
    print("PROCESSING FINISHED")
    print("=" * 80)


if __name__ == "__main__":
    main()