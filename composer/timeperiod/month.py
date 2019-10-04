from ..errors import PlannerIsInTheFutureError
from .base import Period
from .day import Day


class _Month(Period):

    duration = 4 * 7 * 24 * 60 * 60

    def advance_criteria_met(self, to_date, now):
        """ Have criteria for advancement to the next month been met?

        :param :class:`datetime.date` to_date: The date to advance to
        :param :class:`datetime.datetime` now: The time to treat as current
            real world time
        :returns bool: Whether the criteria have been met
        """
        try:
            day_criteria_met = Day.advance_criteria_met(to_date, now)
        except PlannerIsInTheFutureError:
            raise
        if to_date.day == 1 and day_criteria_met:
            return True
        else:
            return False

    def get_name(self):
        return "month"


Month = _Month()
