import abc

ABC = abc.ABCMeta('ABC', (object,), {})  # compatible with Python 2 *and* 3


class PlannerBase(ABC):
    date = None

    # @abc.abstractmethod
    # def construct(location):
    #     raise NotImplementedError

    # @abc.abstractmethod
    # def save():
    #     raise NotImplementedError
