from ..errors import PlannerIsInTheFutureError
from .utils import get_next_day
from .base import Period
from .day import Day
from .quarter import Quarter

FIRST_MONTH_OF_YEAR = "january"


class _Year(Period):

    duration = 4 * 3 * 4 * 7 * 24 * 60 * 60

    def advance_criteria_met(self, planner_date, now):
        """ Have criteria for advancement to the next year been met?

        :param :class:`datetime.date` planner_date: The current date of the
            planner
        :param :class:`datetime.datetime` now: The time to treat as current
            real world time
        :returns bool: Whether the criteria have been met
        """
        next_day = get_next_day(planner_date)
        month = next_day.strftime("%B")
        try:
            Day.advance_criteria_met(planner_date, now)
        except PlannerIsInTheFutureError:
            raise
        if (
            Quarter.advance_criteria_met(planner_date, now)
            and month.lower() == FIRST_MONTH_OF_YEAR
        ):
            return True
        else:
            return False

    def get_name(self):
        return "year"


Year = _Year()
