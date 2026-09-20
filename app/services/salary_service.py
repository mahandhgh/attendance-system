from decimal import Decimal, ROUND_HALF_UP
from app.models.salary import SalaryCalculation


class SalaryService:
    def __init__(self, policy):
        self.policy = policy

    def _hours_to_decimal(self, delta):
        seconds = Decimal(str(delta.total_seconds()))

        return seconds / Decimal("3600")

    def _money(self, value):
        return value.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def calculate(self, report, hourly_rate):
        hourly_rate = Decimal(str(hourly_rate))

        overtime_hours = self._hours_to_decimal(report.total_overtime)
        shortage_hours = self._hours_to_decimal(report.total_shortage)
        excess_leave_hours = self._hours_to_decimal(report.total_excess_leave_time)

        overtime_pay = (
            overtime_hours
            * hourly_rate
            * Decimal(str(self.policy.overtime_multiplier))
        )

        shortage_deduction = (
            shortage_hours
            * hourly_rate
            * Decimal(str(self.policy.shortage_multiplier))
        )

        excess_leave_deduction = (
            excess_leave_hours
            * hourly_rate
            * Decimal(str(self.policy.excess_leave_multiplier))
        )

        total_deduction = shortage_deduction + excess_leave_deduction

        net_adjustment = overtime_pay - total_deduction

        return SalaryCalculation(
            employee_id=report.employee_id,
            hourly_rate=self._money(hourly_rate),
            overtime_hours=overtime_hours,
            overtime_pay=self._money(overtime_pay),
            shortage_hours=shortage_hours,
            shortage_deduction=self._money(shortage_deduction),
            excess_leave_hours=excess_leave_hours,
            excess_leave_deduction=self._money(excess_leave_deduction),
            total_deduction=self._money(total_deduction),
            net_adjustment=self._money(net_adjustment)
        )
