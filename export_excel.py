from pathlib import Path
from app.database.init_db import init_database
from app.readers.attendance_reader import AttendanceReader
from app.services.dataset_processing_service import DatasetProcessingService
from app.services.excel_export_service import ExcelExportService
from app.services.final_report_service import FinalReportService
from app.services.salary_rate_service import SalaryRateService
from app.services.salary_service import SalaryService
from app.config.salary_policy import DEFAULT_SALARY_POLICY
from app.database.connection import SessionLocal


def main():

    init_database()

    reader = AttendanceReader()

    df = reader.read(
        Path("data/HR.TXT")
    )

    processor = DatasetProcessingService()

    monthly_reports = processor.process(df)

    session = SessionLocal()

    try:
        hourly_rates = (
            SalaryRateService()
            .get_all_rates(session)
        )

    finally:
        session.close()

    salary_service = SalaryService(
        policy=DEFAULT_SALARY_POLICY
    )

    final_service = FinalReportService(
        salary_service=salary_service
    )

    final_reports = final_service.build(
        monthly_reports=monthly_reports,
        hourly_rates=hourly_rates,
        default_hourly_rate=0,
    )

    output_dir = Path("output")
    output_dir.mkdir(
        exist_ok=True
    )

    output_path = (
        output_dir
        / "attendance_monthly_report.xlsx"
    )

    ExcelExportService().export(
        final_reports=final_reports,
        output_path=output_path,
    )

    print(
        f"Excel report created: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()