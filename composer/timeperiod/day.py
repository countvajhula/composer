from ..errors import PlannerIsInTheFutureError
from .base import Period


class _Day(Period):

    duration = 24 * 60 * 60

    def advance_criteria_met(self, planner_date, now):
        today = now.date()
        if planner_date < today:
            return True
        if planner_date == today:
            if now.hour >= 18:
                return True
            else:
                # current day still in progress
                return False
        else:
            # planner is in the future
            raise PlannerIsInTheFutureError("Planner is in the future!")

    def get_name(self):
        return "day"


Day = _Day()
