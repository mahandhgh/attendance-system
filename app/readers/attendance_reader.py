from pathlib import Path

import pandas as pd

from app.utils.date_utils import parse_jalali_date


class AttendanceReader:
    REQUIRED_COLUMNS = ["id", "hour", "date", "x", "y", "z"]

    def read(self, file_path: str | Path) -> pd.DataFrame:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Attendance file not found: {file_path}"
            )

        df = pd.read_csv(
            file_path,
            header=None,
            dtype=str
        )

        if df.shape[1] < 3:
            raise ValueError(
                "Attendance file must contain at least 3 columns."
            )

        df.columns = self.REQUIRED_COLUMNS[:df.shape[1]]

        df["id"] = df["id"].astype(str).str.strip()

        df["date"] = df["date"].apply(parse_jalali_date)

        df["hour"] = pd.to_timedelta(
            df["hour"].astype(str).str.strip(),
            errors="coerce"
        )

        df = df.dropna(
            subset=["id", "date", "hour"]
        )

        return df