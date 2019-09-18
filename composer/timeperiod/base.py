import abc
import datetime

from datetime import timedelta

ABC = abc.ABCMeta("ABC", (object,), {})  # compatible with Python 2 *and* 3


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
    def advance_criteria_met(self, planner_date, now):
        raise NotImplementedError

    @abc.abstractmethod
    def get_name(self):
        raise NotImplementedError

    def get_start_date(self, planner_date):
        now = datetime.datetime.now()
        current_date = planner_date
        previous_date = current_date - timedelta(days=1)
        while not self.advance_criteria_met(previous_date, now):
            current_date = previous_date
            previous_date -= timedelta(days=1)
        return current_date

    def get_end_date(self, planner_date):
        now = datetime.datetime.now()
        current_date = planner_date
        while not self.advance_criteria_met(current_date, now):
            current_date += timedelta(days=1)
        return current_date



class _Zero(Period):

    duration = 0

    def advance_criteria_met(self, planner_date, now):
        """ A null period for 'algebraic' convenience. """
        raise NotImplementedError

    def get_name(self):
        """ A null period for 'algebraic' convenience. """
        raise NotImplementedError


Zero = _Zero()
