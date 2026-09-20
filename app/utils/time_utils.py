from datetime import timedelta


def format_timedelta(value: timedelta) -> str:
    """
    Convert timedelta to HH:MM:SS.

    Examples:
        2:30:15   -> 02:30:15
        1 day     -> 24:00:00
        7 days 18h -> 186:00:00
    """

    if value is None:
        return "00:00:00"

    total_seconds = int(value.total_seconds())

    sign = "-" if total_seconds < 0 else ""
    total_seconds = abs(total_seconds)

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"