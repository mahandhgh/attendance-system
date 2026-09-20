from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class WorkSchedule:
    saturday_to_wednesday_start: time = time(9, 0)
    saturday_to_wednesday_end: time = time(17, 0)

    thursday_start: time = time(9, 0)
    thursday_end: time = time(14, 0)

    allowed_late_until: time = time(9, 15)


DEFAULT_SCHEDULE = WorkSchedule()