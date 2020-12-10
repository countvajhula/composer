import calendar

from .base import Period
from .day import Day
from .month import Month

MIN_WEEK_LENGTH = 5


class _Week(Period):

    duration = 7 * 24 * 60 * 60

    def is_start_of_period(self, to_date):
        """Have criteria for advancement to the next week been met?

        :param :class:`datetime.date` to_date: The date to advance to
        :returns bool: Whether the criteria have been met
        """
        dow = to_date.strftime("%A")
        year = to_date.year
        day_criteria_met = Day.is_start_of_period(to_date)
        if Month.is_start_of_period(to_date) or (
            day_criteria_met
            and dow.lower() == "sunday"
            and to_date.day > MIN_WEEK_LENGTH
            and calendar.monthrange(year, to_date.month)[1] - to_date.day + 1
            >= MIN_WEEK_LENGTH
        ):
            return True
        else:
            return False

    def get_name(self):
        return "week"


Week = _Week()
