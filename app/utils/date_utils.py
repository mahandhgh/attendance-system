import jdatetime
from datetime import date, timedelta


def parse_jalali_date(value: str) -> date:
    value = str(value).strip()

    jalali_date = jdatetime.datetime.strptime(
        value,
        "%Y/%m/%d"
    ).date()

    return jalali_date.togregorian()


def jalali_year(value: date) -> int:
    return jdatetime.date.fromgregorian(
        date=value
    ).year


def jalali_month(value: date) -> int:
    return jdatetime.date.fromgregorian(
        date=value
    ).month

def jalali_year_month(value: date) -> tuple[int, int]:
    jalali = jdatetime.date.fromgregorian(
        date=value
    )
    return jalali.year, jalali.month

def jalali_year_start_end(year: int):
    start = jdatetime.date(year, 1, 1).togregorian()
    next_year_start = jdatetime.date(year+1, 1, 1).togregorian()

    end = next_year_start - timedelta(days=1)

    return start, end