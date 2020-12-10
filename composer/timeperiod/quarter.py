from .base import Period
from .month import Month

FIRST_MONTH_IN_QUARTER = {1, 4, 7, 10}


class _Quarter(Period):

    duration = 3 * 4 * 7 * 24 * 60 * 60

    def is_start_of_period(self, to_date):
        """Have criteria for advancement to the next quarter been met?

        :param :class:`datetime.date` to_date: The date to advance to
        :returns bool: Whether the criteria have been met
        """
        if (
            Month.is_start_of_period(to_date)
            and to_date.month in FIRST_MONTH_IN_QUARTER
        ):
            return True
        else:
            return False

    def get_name(self):
        return "quarter"


Quarter = _Quarter()
