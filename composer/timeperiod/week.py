import calendar

from ..errors import PlannerIsInTheFutureError
from .base import Period
from .day import Day
from .month import Month

MIN_WEEK_LENGTH = 5


class _Week(Period):

    duration = 7 * 24 * 60 * 60

    def advance_criteria_met(self, to_date, now):
        """ Have criteria for advancement to the next week been met?

        :param :class:`datetime.date` to_date: The date to advance to
        :param :class:`datetime.datetime` now: The time to treat as current
            real world time
        :returns bool: Whether the criteria have been met
        """
        # note that this is checking whether the planner is ~ready for~ an
        # advance, not whether its current state already represents an advance
        dow = to_date.strftime("%A")
        year = to_date.year
        try:
            day_criteria_met = Day.advance_criteria_met(to_date, now)
        except PlannerIsInTheFutureError:
            raise
        if Month.advance_criteria_met(to_date, now) or (
            day_criteria_met
            and dow.lower() == "sunday"
            and to_date.day > MIN_WEEK_LENGTH
            and calendar.monthrange(year, to_date.month)[1]
            - to_date.day + 1
            >= MIN_WEEK_LENGTH
        ):
            return True
        else:
            return False

    def get_name(self):
        return "week"


Week = _Week()
