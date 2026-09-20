from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum


class AttendanceStatus(Enum):
    ABSENT = "absent"
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"
    MULTIPLE_PUNCHES = "multiple_punches"


@dataclass
class AttendanceRecord:
    employee_id: str
    work_date: date
    punch_time: timedelta


@dataclass
class DailyAttendance:
    employee_id: str
    work_date: date
    punches: list[timedelta]

    @property
    def status(self) -> AttendanceStatus:
        count = len(self.punches)

        if count == 0:
            return AttendanceStatus.ABSENT

        if count == 1:
            return AttendanceStatus.INCOMPLETE

        if count == 2:
            return AttendanceStatus.COMPLETE

        return AttendanceStatus.MULTIPLE_PUNCHES