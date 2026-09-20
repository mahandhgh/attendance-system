from app.models.attendance_log import AttendanceLog


class AttendanceRepository:
    def get_existing_keys(self, session):
        records = session.query(
            AttendanceLog.employee_id,
            AttendanceLog.work_date,
            AttendanceLog.punch_time
        ).all()

        return {
            (
                record.employee_id,
                record.work_date,
                record.punch_time
            )
            for record in records
        }

    def save_logs(self, session, logs):
        if not logs:
            return
        
        session.add_all(logs)
        session.commit()
        