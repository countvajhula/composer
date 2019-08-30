from __future__ import absolute_import
from ..errors import PlannerIsInTheFutureError
from .base import Period


class _Day(Period):

    duration = 24 * 60 * 60

    def advance_criteria_met(self, planner, now):
        today = now.date()
        if planner.date < today:
            return True
        if planner.date == today:
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
