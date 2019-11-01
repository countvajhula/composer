from .base import Period


class _Day(Period):

    duration = 24 * 60 * 60

    def is_start_of_period(self, to_date):
        """ Have criteria for advancement to the next day been met?

        :param :class:`datetime.date` to_date: The date to advance to
        :returns bool: Whether the criteria have been met
        """
        return True

    def get_name(self):
        return "day"


Day = _Day()
