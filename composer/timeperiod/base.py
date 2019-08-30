import abc

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
    def advance_criteria_met(self, planner, now):
        raise NotImplementedError

    @abc.abstractmethod
    def get_name(self):
        raise NotImplementedError


class _Zero(Period):

    duration = 0

    def advance_criteria_met(self, planner, now):
        """ A null period for 'algebraic' convenience. """
        raise NotImplementedError

    def get_name(self):
        """ A null period for 'algebraic' convenience. """
        raise NotImplementedError


Zero = _Zero()
