from decimal import Decimal
from pathlib import Path
import sys
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from app.config.salary_policy import DEFAULT_SALARY_POLICY
from app.database.connection import SessionLocal
from app.models.leave import Leave, LeaveType
from app.readers.attendance_reader import AttendanceReader
from app.services.dataset_processing_service import DatasetProcessingService
from app.services.final_report_service import FinalReportService
from app.services.leave_service import LeaveService
from app.services.salary_rate_service import SalaryRateService
from app.services.salary_service import SalaryService
from app.utils.date_utils import parse_jalali_date
from app.utils.time_utils import format_timedelta


def get_app_directory():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Attendance & Payroll System"
        )

        self.resize(1100, 750)

        self.df = None
        self.final_reports = []

        self.salary_rate_service = SalaryRateService()
        self.leave_service = LeaveService()

        self.salary_service = SalaryService(
            policy=DEFAULT_SALARY_POLICY
        )

        self.build_ui()

    def build_ui(self):
        tabs = QTabWidget()

        tabs.addTab(
            self.build_report_tab(),
            "Monthly Report",
        )

        tabs.addTab(
            self.build_leave_tab(),
            "Register Leave",
        )

        self.setCentralWidget(tabs)

    def build_report_tab(self):
        widget = QWidget()

        layout = QVBoxLayout(widget)

        controls = QGroupBox("Report Settings")

        form = QFormLayout()

        self.employee_combo = QComboBox()

        self.month_combo = QComboBox()

        self.hourly_rate_input = QDoubleSpinBox()

        self.hourly_rate_input.setRange(0, 999999999999)

        self.hourly_rate_input.setDecimals(2)

        self.hourly_rate_input.setValue(0)

        self.employee_combo.currentTextChanged.connect(
            self.load_employee_salary_rate
        )

        form.addRow(
            "Employee:",
            self.employee_combo,
        )

        form.addRow(
            "Month:",
            self.month_combo,
        )

        form.addRow(
            "Hourly Rate:",
            self.hourly_rate_input,
        )

        controls.setLayout(form)

        layout.addWidget(controls)

        button_layout = QHBoxLayout()

        load_button = QPushButton(
            "Load Attendance Data"
        )

        load_button.clicked.connect(
            self.load_data
        )

        calculate_button = QPushButton(
            "Calculate Report"
        )

        calculate_button.clicked.connect(
            self.show_selected_report
        )

        save_rate_button = QPushButton(
            "Save Salary Rate"
        )

        save_rate_button.clicked.connect(
            self.save_salary_rate
        )

        button_layout.addWidget(
            load_button
        )

        button_layout.addWidget(
            calculate_button
        )

        button_layout.addWidget(
            save_rate_button
        )

        layout.addLayout(button_layout)

        self.report_table = QTableWidget()

        self.report_table.setColumnCount(2)

        self.report_table.setHorizontalHeaderLabels(
            [
                "Item",
                "Value",
            ]
        )

        self.report_table.horizontalHeader() \
            .setStretchLastSection(True)

        layout.addWidget(
            self.report_table
        )

        return widget

    def build_leave_tab(self):
        widget = QWidget()

        layout = QVBoxLayout(widget)

        form_box = QGroupBox("Leave Registration")

        form = QFormLayout()

        self.leave_employee_input = QLineEdit()

        self.leave_date_input = QLineEdit()

        self.leave_date_input.setPlaceholderText("1405/03/10")

        self.leave_type_combo = QComboBox()

        self.leave_type_combo.addItem(
            "Annual Leave",
            LeaveType.ANNUAL,
        )

        self.leave_type_combo.addItem(
            "Sick Leave",
            LeaveType.SICK,
        )

        self.leave_type_combo.addItem(
            "Hourly Leave",
            LeaveType.HOURLY,
        )

        self.leave_duration_input = QDoubleSpinBox()

        self.leave_duration_input.setRange(0.25, 24 * 30)

        self.leave_duration_input.setSingleStep(0.25)

        self.leave_duration_input.setDecimals(2)

        self.leave_description_input = QLineEdit()

        form.addRow(
            "Employee ID:",
            self.leave_employee_input,
        )

        form.addRow(
            "Jalali Date:",
            self.leave_date_input,
        )

        form.addRow(
            "Leave Type:",
            self.leave_type_combo,
        )

        form.addRow(
            "Duration (hours):",
            self.leave_duration_input,
        )

        form.addRow(
            "Description:",
            self.leave_description_input,
        )

        form_box.setLayout(form)

        layout.addWidget(form_box)

        save_leave_button = QPushButton("Register Leave")

        save_leave_button.clicked.connect(
            self.register_leave
        )

        layout.addWidget(
            save_leave_button
        )

        info = QLabel(
            "Hourly leave is currently not deducted "
            "from required monthly time."
        )

        info.setWordWrap(True)

        layout.addWidget(info)

        layout.addStretch()

        return widget

    def load_data(self):
        try:
            reader = AttendanceReader()

            app_dir = get_app_directory()

            attendance_file = (
                app_dir/ "data"/ "HR.TXT")

            self.df = reader.read(attendance_file)

            processor = DatasetProcessingService()

            monthly_reports = processor.process(
                self.df
            )

            session = SessionLocal()

            try:
                hourly_rates = (
                    self.salary_rate_service
                    .get_all_rates(
                        session=session
                    )
                )

            finally:
                session.close()

            self.final_reports = (
                FinalReportService(
                    salary_service=self.salary_service
                )
                .build(
                    monthly_reports=monthly_reports,
                    hourly_rates=hourly_rates,
                    default_hourly_rate=Decimal("0"),
                )
            )

            self.populate_filters()

            QMessageBox.information(
                self,
                "Success",
                "Attendance data loaded successfully.",
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Error",
                str(exc),
            )

    def populate_filters(self):
        self.employee_combo.blockSignals(True)

        self.employee_combo.clear()

        self.month_combo.clear()

        employees = sorted(
            {
                item.attendance_report.employee_id
                for item in self.final_reports
            }
        )

        for employee_id in employees:
            self.employee_combo.addItem(employee_id)

        months = sorted(
            {
                (
                    item.year,
                    item.month,
                )
                for item in self.final_reports
            }
        )

        for year, month in months:

            self.month_combo.addItem(
                f"{year}/{month:02d}",
                (year, month),
            )

        self.employee_combo.blockSignals(False)

        if self.employee_combo.count() > 0:

            self.load_employee_salary_rate(
                self.employee_combo.currentText()
            )

    def load_employee_salary_rate(self, employee_code):
        employee_code = (
            employee_code.strip()
        )

        if not employee_code:
            return

        session = SessionLocal()

        try:

            rate = (
                self.salary_rate_service
                .get_rate(
                    session=session,
                    employee_code=employee_code,
                )
            )

            if rate is None:
                self.hourly_rate_input.setValue(0)

            else:
                self.hourly_rate_input.setValue(float(rate))

        except Exception as exc:

            QMessageBox.warning(
                self,
                "Warning",
                f"Could not load salary rate:\n{exc}",
            )

        finally:

            session.close()

    def save_salary_rate(self):
        employee_code = (
            self.employee_combo
            .currentText()
            .strip()
        )

        if not employee_code:

            QMessageBox.warning(
                self,
                "Warning",
                "Select an employee first.",
            )
            return

        hourly_rate = Decimal(
            str(
                self.hourly_rate_input.value()
            )
        )

        if hourly_rate < 0:

            QMessageBox.warning(
                self,
                "Warning",
                "Hourly rate cannot be negative.",
            )

            return

        session = SessionLocal()

        try:

            self.salary_rate_service.save_rate(
                session=session,
                employee_code=employee_code,
                hourly_rate=hourly_rate,
            )

            QMessageBox.information(
                self,
                "Success",
                "Salary rate saved successfully.",
            )

            self.refresh_final_reports()

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Error",
                str(exc),
            )

        finally:

            session.close()

    def refresh_final_reports(self):
        if self.df is None:
            return

        try:

            processor = DatasetProcessingService()

            monthly_reports = (
                processor.process(
                    self.df
                )
            )

            session = SessionLocal()

            try:

                hourly_rates = (
                    self.salary_rate_service
                    .get_all_rates(
                        session=session
                    )
                )

            finally:
                session.close()

            self.final_reports = (
                FinalReportService(
                    salary_service=self.salary_service
                )
                .build(
                    monthly_reports=monthly_reports,
                    hourly_rates=hourly_rates,
                    default_hourly_rate=Decimal("0"),
                )
            )

            self.populate_filters()

        except Exception as exc:

            QMessageBox.warning(
                self,
                "Warning",
                f"Could not refresh reports:\n{exc}",
            )

    def get_selected_report(self):
        if not self.final_reports:

            return None

        employee_id = (
            self.employee_combo
            .currentText()
            .strip()
        )

        month_data = (
            self.month_combo
            .currentData()
        )

        if month_data is None:

            return None

        year, month = month_data

        for item in self.final_reports:

            report = item.attendance_report

            if (
                report.employee_id == employee_id
                and item.year == year
                and item.month == month
            ):

                return item

        return None

    def show_selected_report(self):
        if not self.final_reports:

            QMessageBox.warning(
                self,
                "Warning",
                "Load attendance data first.",
            )

            return

        selected = (
            self.get_selected_report()
        )

        if selected is None:

            QMessageBox.warning(
                self,
                "Warning",
                "Report not found.",
            )

            return

        report = selected.attendance_report

        employee_code = (report.employee_id)

        hourly_rate = Decimal(
            str(
                self.hourly_rate_input.value()
            )
        )

        salary = (
            self.salary_service.calculate(
                report=report,
                hourly_rate=hourly_rate,
            )
        )

        rows = [
            (
                "Required Time",
                format_timedelta(
                    report.total_required_time
                ),
            ),

            (
                "Worked Time",
                format_timedelta(
                    report.total_worked_time
                ),
            ),

            (
                "Overtime",
                format_timedelta(
                    report.total_overtime
                ),
            ),

            (
                "Shortage",
                format_timedelta(
                    report.total_shortage
                ),
            ),

            (
                "Delay",
                format_timedelta(
                    report.total_delay
                ),
            ),

            (
                "Leave Time",
                format_timedelta(
                    report.total_leave_time
                ),
            ),

            (
                "Allowed Leave",
                format_timedelta(
                    report.total_allowed_leave_time
                ),
            ),

            (
                "Excess Leave",
                format_timedelta(
                    report.total_excess_leave_time
                ),
            ),

            (
                "Work Days",
                str(
                    report.work_days
                ),
            ),

            (
                "Absent Days",
                str(
                    report.absent_days
                ),
            ),

            (
                "Incomplete Days",
                str(
                    report.incomplete_days
                ),
            ),

            (
                "Multiple Punch Days",
                str(
                    report.multiple_punch_days
                ),
            ),

            (
                "Holiday Days",
                str(
                    report.holiday_days
                ),
            ),

            (
                "Leave Days",
                str(
                    report.leave_days
                ),
            ),

            (
                "Hourly Rate",
                str(
                    salary.hourly_rate
                ),
            ),

            (
                "Overtime Hours",
                str(
                    salary.overtime_hours
                ),
            ),

            (
                "Overtime Pay",
                str(
                    salary.overtime_pay
                ),
            ),

            (
                "Shortage Hours",
                str(
                    salary.shortage_hours
                ),
            ),

            (
                "Shortage Deduction",
                str(
                    salary.shortage_deduction
                ),
            ),

            (
                "Excess Leave Hours",
                str(
                    salary.excess_leave_hours
                ),
            ),

            (
                "Excess Leave Deduction",
                str(
                    salary.excess_leave_deduction
                ),
            ),

            (
                "Total Deduction",
                str(
                    salary.total_deduction
                ),
            ),

            (
                "Net Adjustment",
                str(
                    salary.net_adjustment
                ),
            ),
        ]

        self.report_table.setRowCount(
            len(rows)
        )

        for row_index, (name, value) in enumerate(rows):
            self.report_table.setItem(
                row_index,
                0,
                QTableWidgetItem(name),
            )

            self.report_table.setItem(
                row_index,
                1,
                QTableWidgetItem(value),
            )

        self.report_table.resizeColumnsToContents()

    def register_leave(self):
        employee_code = (
            self.leave_employee_input
            .text()
            .strip()
        )

        jalali_date = (
            self.leave_date_input
            .text()
            .strip()
        )

        leave_type = (
            self.leave_type_combo
            .currentData()
        )

        duration = (
            self.leave_duration_input
            .value()
        )

        description = (
            self.leave_description_input
            .text()
            .strip()
        )

        if not employee_code:
            QMessageBox.warning(
                self,
                "Warning",
                "Employee ID is required.",
            )

            return

        try:
            leave_date = (
                parse_jalali_date(
                    jalali_date
                )
            )

        except Exception:

            QMessageBox.warning(
                self,
                "Warning",
                "Invalid Jalali date.",
            )

            return

        session = SessionLocal()

        try:
            leave = Leave(
                employee_code=employee_code,
                leave_date=leave_date,
                leave_type=leave_type,
                duration_hours=duration,
                description=description,
            )

            self.leave_service.add_leave(
                session=session,
                leave=leave,
            )

            QMessageBox.information(
                self,
                "Success",
                "Leave registered successfully.",
            )

            self.leave_date_input.clear()

            self.leave_duration_input.setValue(
                1
            )

            self.leave_description_input.clear()

            self.refresh_final_reports()

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Error",
                str(exc),
            )

        finally:

            session.close()