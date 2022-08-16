import abc
import datetime

from datetime import timedelta

ABC = abc.ABCMeta("ABC", (object,), {})  # compatible with Python 2 *and* 3

INFINITY = float('inf')


class Period(ABC):
    def __lt__(self, other):
        return self.duration < other.duration

    def __le__(self, other):
        return self.duration <= other.duration

    def __eq__(self, other):
        return self.duration == other.duration

    def __ne__(self, other):
        return self.duration != other.duration

    def __gt__(self, other):
        return self.duration > other.duration

    def __ge__(self, other):
        return self.duration >= other.duration

    def __key(self):
        return self.duration

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return self.get_name()

    @abc.abstractmethod
    def is_start_of_period(self, to_date):
        raise NotImplementedError

    @abc.abstractmethod
    def get_name(self):
        raise NotImplementedError

    def get_start_date(self, for_date):
        """Given a date, return the date corresponding to the
        start of the present period (e.g. Week) encompassing that date.

        :param :class:`datetime.date` for_date: The reference date
        :returns :class:`datetime.date`: The start date of the concerned period
        """
        current_date = for_date
        previous_date = current_date - timedelta(days=1)
        while not self.is_start_of_period(current_date):
            current_date = previous_date
            previous_date -= timedelta(days=1)
        return current_date

    def get_end_date(self, for_date):
        """Given a date, return the date corresponding to the
        end of the present period (e.g. Week) encompassing that date.

        :param :class:`datetime.date` for_date: The reference date
        :returns :class:`datetime.date`: The end date of the concerned period
        """
        current_date = for_date
        next_date = current_date + timedelta(days=1)
        while not self.is_start_of_period(next_date):
            current_date = next_date
            next_date += timedelta(days=1)
        return current_date


class _Zero(Period):

    duration = 0

    def is_start_of_period(self, to_date):
        """A null period for 'algebraic' convenience."""
        return True

    def get_name(self):
        """A null period for 'algebraic' convenience."""
        return "zero"

    def get_start_date(self, for_date):
        """Given a date, return the date corresponding to the
        start of the present period (e.g. Week) encompassing that date.

        :param :class:`datetime.date` for_date: The reference date
        :returns :class:`datetime.date`: The start date of the concerned period
        """
        # TODO: this is a hack to prevent this period from being "relevant" for
        # scheduling purposes. it is probably going to cause bugs. maybe treat
        # Day (i.e. lowest tracked period) as null instead and eliminate Zero?
        return datetime.date(1, 1, 1)

    def get_end_date(self, for_date):
        """Given a date, return the date corresponding to the
        end of the present period (e.g. Week) encompassing that date.

        :param :class:`datetime.date` for_date: The reference date
        :returns :class:`datetime.date`: The end date of the concerned period
        """
        # TODO: this is a hack to prevent this period from being "relevant" for
        # scheduling purposes. it is probably going to cause bugs. maybe treat
        # Day (i.e. lowest tracked period) as null instead and eliminate Zero?
        return datetime.date(1, 1, 1)


Zero = _Zero()


class _Eternity(Period):

    duration = INFINITY

    def is_start_of_period(self, to_date=None):
        """An infinite period for 'algebraic' convenience."""
        return True

    def get_name(self):
        """An infinite period for 'algebraic' convenience."""
        return "eternity"

    def get_start_date(self, for_date=None):
        """Given a date, return the date corresponding to the
        start of the present period (e.g. Week) encompassing that date.

        :param :class:`datetime.date` for_date: The reference date
        :returns :class:`datetime.date`: The start date of the concerned period
        """
        return datetime.date(1, 1, 1)

    def get_end_date(self, for_date=None):
        """Given a date, return the date corresponding to the
        end of the present period (e.g. Week) encompassing that date.

        :param :class:`datetime.date` for_date: The reference date
        :returns :class:`datetime.date`: The end date of the concerned period
        """
        return datetime.date(9999, 12, 12)


Eternity = _Eternity()
