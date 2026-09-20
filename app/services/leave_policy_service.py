from collections import defaultdict

class LeavePolicyService:
    def __init__(self, policy):
        self.policy = policy

    def calculate_annual_excess_by_month(self, monthly_statistics):
        result = {}

        annual_allowed_hours = (
            self.policy.annual_leave_days_per_year
            * self.policy.standard_daily_hours
        )

        cumulative_annual = 0.0
        previous_annual_excess = 0.0

        cumulative_sick = 0.0
        previous_sick_excess = 0.0

        if self.policy.sick_leave_days_per_year is None:
            sick_allowed_hours = None
        else:
            sick_allowed_hours = (
                self.policy.sick_leave_days_per_year
                * self.policy.standard_daily_hours
            )

        for month_key in sorted(monthly_statistics):
            statistics = monthly_statistics[month_key]

            annual_hours = float(statistics.get("annual_hours", 0.0))

            sick_hours = float(statistics.get("sick_hours", 0.0))

            hourly_hours = float(statistics.get("hourly_hours", 0.0))

            cumulative_annual += annual_hours

            current_annual_excess = max(0.0, cumulative_annual - annual_allowed_hours)

            annual_excess_this_month = (current_annual_excess - previous_annual_excess)

            previous_annual_excess = current_annual_excess

            if sick_allowed_hours is None:
                sick_excess_this_month = 0.0
            else:
                cumulative_sick += sick_hours

                current_sick_excess = max(0.0, cumulative_sick - sick_allowed_hours)

                sick_excess_this_month = current_sick_excess - previous_sick_excess

                previous_sick_excess = current_sick_excess

            hourly_excess_this_month = 0.0

            total_excess = (
                annual_excess_this_month
                + sick_excess_this_month
                + hourly_excess_this_month
            )

            result[month_key] = {
                "annual_excess_hours": (
                    annual_excess_this_month
                ),
                "sick_excess_hours": (
                    sick_excess_this_month
                ),
                "hourly_excess_hours": (
                    hourly_excess_this_month
                ),
                "total_excess_hours": total_excess,
            }

        return result