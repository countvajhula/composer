from .base import Period


class _Month(Period):

    duration = 4 * 7 * 24 * 60 * 60

    def is_start_of_period(self, to_date):
        """ Have criteria for advancement to the next month been met?

        :param :class:`datetime.date` to_date: The date to advance to
        :returns bool: Whether the criteria have been met
        """
        if to_date.day == 1:
            return True
        else:
            return False

    def get_name(self):
        return "month"


Month = _Month()
