from ..errors import PlannerIsInTheFutureError
from .base import Period
from .day import Day
from .quarter import Quarter

FIRST_MONTH_OF_YEAR = "january"


class _Year(Period):

    duration = 4 * 3 * 4 * 7 * 24 * 60 * 60

    def advance_criteria_met(self, to_date, now):
        """ Have criteria for advancement to the next year been met?

        :param :class:`datetime.date` to_date: The date to advance to
        :param :class:`datetime.datetime` now: The time to treat as current
            real world time
        :returns bool: Whether the criteria have been met
        """
        month = to_date.strftime("%B")
        try:
            Day.advance_criteria_met(to_date, now)
        except PlannerIsInTheFutureError:
            raise
        if (
            Quarter.advance_criteria_met(to_date, now)
            and month.lower() == FIRST_MONTH_OF_YEAR
        ):
            return True
        else:
            return False

    def get_name(self):
        return "year"


Year = _Year()
