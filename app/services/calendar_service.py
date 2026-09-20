from dataclasses import dataclass
from datetime import date
from pathlib import Path
import json
import time

import jdatetime
import requests

from app.config.settings import DEFAULT_SCHEDULE


@dataclass
class CalendarDay:
    date: date
    weekday_symbol: str
    weekday_name: str
    is_friday: bool
    is_holiday: bool
    required_hours: float


class CalendarService:

    API_URL = "https://pnldev.com/api/calender"

    WEEKDAY_NAMES = {
        "ش": "Saturday",
        "ی": "Sunday",
        "د": "Monday",
        "س": "Tuesday",
        "چ": "Wednesday",
        "پ": "Thursday",
        "ج": "Friday",
    }

    CACHE_DIR = Path("data/calendar_cache")

    def __init__(self):
        self.CACHE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    def get_month_days(
        self,
        year: int,
        month: int
    ) -> list[CalendarDay]:

        cache_file = self._get_cache_file(year, month)

        if cache_file.exists():
            data = self._load_cache(cache_file)
        else:
            data = self._fetch_from_api(year, month)

            self._save_cache(cache_file, data)

        return self._parse_calendar_data(data)

    def _get_cache_file(self, year: int, month: int) -> Path:
        return self.CACHE_DIR / (
            f"{year}_{month:02d}.json"
        )

    def _fetch_from_api(self, year: int, month: int, max_retries: int = 3):
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(
                    self.API_URL,
                    params={
                        "year": year,
                        "month": month,
                    },
                    timeout=(10, 60),
                )

                response.raise_for_status()
                data = response.json()

                if data.get("status") is False:
                    raise RuntimeError(
                        data.get(
                            "result",
                            "Calendar API error"
                        )
                    )
                return data

            except (
                requests.RequestException,
                RuntimeError
            ) as exc:

                last_error = exc

                if attempt < max_retries:
                    time.sleep(2)

        raise RuntimeError(
            f"Unable to fetch calendar for "
            f"{year}/{month} after "
            f"{max_retries} attempts."
        ) from last_error

    def _save_cache(self, cache_file: Path, data):
        with cache_file.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )

    def _load_cache(self, cache_file: Path):
        with cache_file.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def _parse_calendar_data(self, data) -> list[CalendarDay]:
        days = []

        for info in data["result"].values():
            solar = info["solar"]

            jalali_date = jdatetime.date(
                int(solar["year"]),
                int(solar["month"]),
                int(solar["day"]),
            )
            gregorian_date = (jalali_date.togregorian())

            weekday_symbol = solar["dayWeek"]

            is_holiday = bool(info["holiday"])

            is_friday = (weekday_symbol == "ج")

            required_hours = (
                self._calculate_required_hours(weekday_symbol, is_holiday)
                )

            days.append(
                CalendarDay(
                    date=gregorian_date,
                    weekday_symbol=weekday_symbol,
                    weekday_name=self.WEEKDAY_NAMES[
                        weekday_symbol
                    ],
                    is_friday=is_friday,
                    is_holiday=is_holiday,
                    required_hours=required_hours,
                )
            )

        days.sort(key=lambda item: item.date)
        return days

    def _calculate_required_hours(self, weekday_symbol: str, is_holiday: bool) -> float:
        if is_holiday:
            return 0.0

        if weekday_symbol == "ج":
            return 0.0

        if weekday_symbol == "پ":
            start = (DEFAULT_SCHEDULE.thursday_start)
            end = (DEFAULT_SCHEDULE.thursday_end)
        else:
            start = (DEFAULT_SCHEDULE.saturday_to_wednesday_start)
            end = (DEFAULT_SCHEDULE.saturday_to_wednesday_end)

        start_minutes = (start.hour * 60 + start.minute)
        end_minutes = (end.hour * 60 + end.minute)

        return (end_minutes - start_minutes) / 60