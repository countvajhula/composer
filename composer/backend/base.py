import abc

ABC = abc.ABCMeta('ABC', (object,), {})  # compatible with Python 2 *and* 3


class PlannerBase(ABC):
    date = None

    @abc.abstractmethod
    def construct(self, location=None):
        raise NotImplementedError

    @abc.abstractmethod
    def advance(self, now=None, simulate=None):
        raise NotImplementedError

    @abc.abstractmethod
    def save(self):
        raise NotImplementedError