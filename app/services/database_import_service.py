from app.repositories.attendance_repository import AttendanceRepository
from app.models.attendance_log import AttendanceLog
from app.repositories.employee_repository import EmployeeRepository


class DatabaseImportService:
    def __init__(self):
        self.attendance_repository = AttendanceRepository()
        self.employee_repository = EmployeeRepository()

    def import_dataframe(self, session, df):
        existing_keys = self.attendance_repository.get_existing_keys(session)

        logs = []
        imported_count = 0
        skipped_count = 0

        for row in df.itertuples(index=False):
            employee = self.employee_repository.get_or_create(session, row.id)
            employee_id = employee.employee_code
            work_date = str(row.date)
            punch_time = str(row.hour)

            key = (employee_id, work_date, punch_time)
            if key in existing_keys:
                skipped_count += 1
                continue

            log = AttendanceLog(
                employee_id=employee_id,
                work_date=work_date,
                punch_time=punch_time
            )
            logs.append(log)
            existing_keys.add(key)

            imported_count += 1

        self.attendance_repository.save_logs(session, logs)

        print(f"New attendance records imported: {imported_count}")
        print(f"Duplicate records skipped: {skipped_count}")