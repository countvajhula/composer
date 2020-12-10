from .base import Period
from .quarter import Quarter

FIRST_MONTH_OF_YEAR = 1


class _Year(Period):

    duration = 4 * 3 * 4 * 7 * 24 * 60 * 60

    def is_start_of_period(self, to_date):
        """Have criteria for advancement to the next year been met?

        :param :class:`datetime.date` to_date: The date to advance to
        :returns bool: Whether the criteria have been met
        """
        if (
            Quarter.is_start_of_period(to_date)
            and to_date.month == FIRST_MONTH_OF_YEAR
        ):
            return True
        else:
            return False

    def get_name(self):
        return "year"


Year = _Year()
