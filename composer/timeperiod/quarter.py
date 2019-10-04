from ..errors import PlannerIsInTheFutureError
from .base import Period
from .day import Day
from .month import Month

FIRST_MONTH_IN_QUARTER = ("january", "april", "july", "october")


class _Quarter(Period):

    duration = 3 * 4 * 7 * 24 * 60 * 60

    def advance_criteria_met(self, to_date, now):
        """ Have criteria for advancement to the next quarter been met?

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
            Month.advance_criteria_met(to_date, now)
            and month.lower() in FIRST_MONTH_IN_QUARTER
        ):
            return True
        else:
            return False

    def get_name(self):
        return "quarter"


Quarter = _Quarter()
