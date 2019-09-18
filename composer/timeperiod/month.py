from ..errors import PlannerIsInTheFutureError
from .base import Period
from .day import Day

from .utils import get_next_day


class _Month(Period):

    duration = 4 * 7 * 24 * 60 * 60

    def advance_criteria_met(self, planner_date, now):
        next_day = get_next_day(planner_date)
        try:
            day_criteria_met = Day.advance_criteria_met(planner_date, now)
        except PlannerIsInTheFutureError:
            raise
        if next_day.day == 1 and day_criteria_met:
            return True
        else:
            return False

    def get_name(self):
        return "month"


Month = _Month()
