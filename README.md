# Attendance & Payroll System

A modular Python-based attendance and payroll management system designed for employee time tracking, leave management, monthly work-hour calculation, salary adjustments, and Excel reporting.

The project is built around a layered architecture with separate readers, models, repositories, services, database components, and a PySide6 desktop interface.

---

## ✨ Features

### Attendance Processing

* Reads fingerprint attendance data from a headerless `HR.TXT` file.
* Handles invalid and missing values.
* Uses employee ID, attendance time, and date as the core attendance fields.
* Converts Persian/Jalali dates to Gregorian dates internally.
* Groups attendance punches by employee and work date.
* Detects:

  * Absent days
  * Incomplete days
  * Complete days
  * Multiple-punch days

### Persian Calendar and Work Schedule

The system uses the Persian/Jalali calendar and retrieves calendar information through an external calendar API.

The default work schedule is:

| Day                | Working Hours |
| ------------------ | ------------: |
| Saturday–Wednesday |   09:00–17:00 |
| Thursday           |   09:00–14:00 |
| Friday             |       0 hours |

Official holidays and Fridays are excluded from required working time.

### Check-in Normalization

Employees who check in between `09:00` and `09:15` are treated as having started work at `09:00` for work-time calculation.

Late arrivals after the allowed window are tracked separately as delay.

### Multiple Punch Handling

The system supports multiple punches during a working day.

For example:

```text
09:00
12:00
13:00
17:00
```

is interpreted as:

```text
09:00 → 12:00
13:00 → 17:00
```

and the two intervals are added together to calculate total worked time.

Unmatched final punches are not guessed as an exit time.

### Monthly Work Balance

For each employee and Persian calendar month, the system calculates:

* Required working time
* Worked time
* Overtime
* Shortage
* Delay
* Leave time
* Allowed leave
* Excess leave
* Work days
* Absent days
* Incomplete days
* Multiple-punch days
* Holiday days
* Leave days

Monthly overtime and shortage are calculated as a net monthly balance, so both values are not positive at the same time.

---

## 🏖️ Leave Management

The system supports three leave types:

* Annual leave
* Sick leave
* Hourly leave

Leave records are stored in the database.

The leave policy is designed separately from the attendance logic, allowing business rules to be changed without rewriting the attendance engine.

### Annual Leave Policy

The default policy defines an annual allowance in hours based on the configured number of annual leave days and standard daily working hours.

Annual leave usage is evaluated cumulatively throughout the Persian calendar year.

This allows excess leave to be identified in the month in which the employee exceeds the annual allowance.

### Hourly Leave

Hourly leave is currently stored and reported separately and does not directly reduce required monthly working time, because its effect is expected to be reflected through the employee's attendance punches.

---

## 💰 Payroll Calculation

Salary calculations are separated from attendance calculations.

The system calculates:

* Hourly rate
* Overtime hours
* Overtime payment
* Shortage hours
* Shortage deduction
* Excess-leave hours
* Excess-leave deduction
* Total deduction
* Net salary adjustment

The salary layer uses `Decimal` for monetary calculations to avoid common floating-point precision problems.

Salary rates are stored in a separate database table rather than modifying the existing employee table.

---

## 🗄️ Database

SQLite is used as the local database and SQLAlchemy is used as the ORM/database access layer.

The database contains information related to:

* Employees
* Attendance logs
* Leaves
* Salary rates

### Duplicate Attendance Protection

Attendance records use the combination of:

```text
employee_id
work_date
punch_time
```

as their logical unique key.

Existing duplicate attendance records can be cleaned, and a database-level unique index prevents the same attendance punch from being inserted again.

This makes repeated imports of the same attendance file safe.

---

## 🖥️ Desktop Interface

The desktop UI is built with PySide6.

The current interface provides:

### Monthly Report

Users can:

* Load attendance data
* Select an employee
* Select a Persian calendar month
* View attendance statistics
* View leave statistics
* View salary calculations
* Enter and save an employee hourly rate

### Leave Registration

Users can register:

* Annual leave
* Sick leave
* Hourly leave

with:

* Employee ID
* Persian date
* Duration
* Description

Reports can then be recalculated from the updated database state.

---

## 📊 Excel Export

Monthly attendance and payroll reports can be exported to `.xlsx`.

The Excel report contains:

* Employee information
* Jalali year/month
* Required and worked time
* Overtime
* Shortage
* Delay
* Leave
* Allowed leave
* Excess leave
* Attendance statistics
* Salary rate
* Overtime payment
* Salary deductions
* Net adjustment

Excel durations are exported as real Excel duration values rather than plain text, allowing further calculations inside Excel.

---

## 🧱 Project Architecture

The project follows a layered and modular structure:

```text
attendance_system/
│
├── app/
│   ├── config/
│   │   ├── leave_policy.py
│   │   ├── salary_policy.py
│   │   └── settings.py
│   │
│   ├── database/
│   │   ├── base.py
│   │   ├── connection.py
│   │   └── init_db.py
│   │
│   ├── models/
│   │   ├── attendance.py
│   │   ├── attendance_log.py
│   │   ├── employee.py
│   │   ├── final_report.py
│   │   ├── leave.py
│   │   ├── monthly_report.py
│   │   ├── salary.py
│   │   └── salary_rate.py
│   │
│   ├── readers/
│   │   └── attendance_reader.py
│   │
│   ├── repositories/
│   │   ├── attendance_repository.py
│   │   ├── employee_repository.py
│   │   ├── leave_repository.py
│   │   └── salary_rate_repository.py
│   │
│   ├── services/
│   │   ├── attendance_calendar_merger.py
│   │   ├── attendance_service.py
│   │   ├── calendar_service.py
│   │   ├── database_import_service.py
│   │   ├── dataset_processing_service.py
│   │   ├── excel_export_service.py
│   │   ├── final_report_service.py
│   │   ├── leave_policy_service.py
│   │   ├── leave_service.py
│   │   ├── monthly_report_service.py
│   │   ├── salary_rate_service.py
│   │   ├── salary_service.py
│   │   └── work_time_service.py
│   │
│   ├── ui/
│   │   └── main_window.py
│   │
│   └── utils/
│       ├── date_utils.py
│       └── time_utils.py
│
├── data/
│   └── HR.TXT
│
├── output/
│
├── main.py
├── run_ui.py
├── export_excel.py
├── attendance.db
├── requirements.txt
└── .gitignore
```

---

## 🔄 Processing Pipeline

The main processing pipeline is:

```text
HR.TXT
   ↓
AttendanceReader
   ↓
Data Cleaning
   ↓
Jalali Date Conversion
   ↓
Attendance Grouping
   ↓
Calendar API
   ↓
Attendance / Calendar Merge
   ↓
Work Time Calculation
   ↓
Multiple Punch Handling
   ↓
Leave Processing
   ↓
Annual Leave Policy
   ↓
Monthly Report
   ↓
Salary Calculation
   ↓
Final Report
   ↓
UI / Excel Export
```

---

## 📥 Input File

The attendance input file is a headerless text file.

The first three logical fields are:

```text
employee_id
hour
date
```

Additional fields may exist in the original device output, but the current application primarily uses:

```text
ID
Time
Date
```

Example:

```text
0000000001,09:10:38,1404/08/19,...
0000000001,15:19:49,1404/08/19,...
```

Place the input file at:

```text
data/HR.TXT
```

---

## ⚙️ Installation

### Requirements

Python 3.13 is recommended for the current project.

Create and activate a virtual environment:

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Initialize the database automatically through the application.

---

## ▶️ Running the Application

### Console processing

```powershell
python main.py
```

### Desktop application

```powershell
python run_ui.py
```

### Excel export

```powershell
python export_excel.py
```

The generated Excel file is saved under:

```text
output/
attendance_monthly_report.xlsx
```

---

## 🧪 Testing

The project was developed incrementally with focused tests covering:

* Leave registration
* Annual leave policy
* Multiple-punch calculation
* Salary calculation
* Salary rate storage

Temporary development test scripts should not be committed to the final GitHub repository.

---

## 📦 Building the Windows Executable

Install PyInstaller:

```powershell
pip install pyinstaller
```

Build the application:

```powershell
pyinstaller --noconfirm --clean --onedir --windowed --name AttendanceSystem run_ui.py
```

The resulting application is created under:

```text
dist/
└── AttendanceSystem/
    └── AttendanceSystem.exe
```

The runtime folder should contain:

```text
AttendanceSystem/
├── AttendanceSystem.exe
├── attendance.db
└── data/
    └── HR.TXT
```

The database and input file remain external to the executable so that application data can persist and input data can be replaced without rebuilding the application.

---

## 🌐 External Calendar API

Calendar information is retrieved through an external Persian calendar API.

The application uses calendar API data for:

* Persian month information
* Weekday information
* Holiday detection

The application should therefore have network access when calendar information is requested.

---

## 🛠️ Configuration

Business rules are separated into configuration modules.

Important configuration areas include:

```text
app/config/settings.py
app/config/leave_policy.py
app/config/salary_policy.py
```

This makes it possible to adjust working hours, leave policies, and salary calculation rules without changing the main processing architecture.

---

## 🚧 Current Limitations

The current version is a strong functional prototype, but some production-level features can still be expanded:

* More advanced leave approval workflows
* Employee management screens
* Detailed daily attendance screens
* Automated backup and database recovery
* Authentication and role-based access
* Richer Excel dashboards
* Automated unit/integration test suite
* More robust API failure/retry handling
* Installation package/installer for end users

---

