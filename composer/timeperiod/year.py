from ..errors import PlannerIsInTheFutureError
from .utils import get_next_day
from .base import Period
from .day import Day
from .quarter import Quarter


class _Year(Period):

    duration = 4 * 3 * 4 * 7 * 24 * 60 * 60

    def advance_criteria_met(self, planner_date, now):
        next_day = get_next_day(planner_date)
        month = next_day.strftime("%B")
        try:
            Day.advance_criteria_met(planner_date, now)
        except PlannerIsInTheFutureError:
            raise
        if (
            Quarter.advance_criteria_met(planner_date, now)
            and month.lower() == "january"
        ):
            return True
        else:
            return False

    def get_name(self):
        return "year"


Year = _Year()
