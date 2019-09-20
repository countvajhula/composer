from ..errors import PlannerIsInTheFutureError
from .base import Period
from .day import Day

from .utils import get_next_day


class _Month(Period):

    duration = 4 * 7 * 24 * 60 * 60

    def advance_criteria_met(self, planner_date, now):
        """ Have criteria for advancement to the next month been met?

        :param :class:`datetime.date` planner_date: The current date of the
            planner
        :param :class:`datetime.datetime` now: The time to treat as current
            real world time
        :returns bool: Whether the criteria have been met
        """
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
