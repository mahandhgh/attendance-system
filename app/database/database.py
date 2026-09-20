import sqlite3


class Database:
    def __init__(self, db_path="attendance.db"):
        self.connection = sqlite3.connect(db_path)

    def create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT UNIQUE NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT,
            work_date DATE,
            hour TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT NOT NULL,
            leave_date DATE NOT NULL,
            leave_type TEXT NOT NULL,
            duration_hours REAL NOT NULL,
            description TEXT
        )
        """)

        self.connection.commit()