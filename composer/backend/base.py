import abc

from ..config import (
    DEFAULT_BULLET_CHARACTER,
    DEFAULT_SCHEDULE,
    LOGFILE_CHECKING,
)

ABC = abc.ABCMeta("ABC", (object,), {})  # compatible with Python 2 *and* 3


class PlannerBase(ABC):
    date = None
    tomorrow_checking = LOGFILE_CHECKING["STRICT"]
    logfile_completion_checking = LOGFILE_CHECKING["STRICT"]
    preferred_bullet_char = DEFAULT_BULLET_CHARACTER
    schedule = DEFAULT_SCHEDULE
    week_theme = None

    def set_preferences(self, preferences=None, jump=False):
        if preferences:
            self.schedule = preferences["schedule"]
            self.preferred_bullet_char = preferences["bullet_character"]

        self.logfile_completion_checking = (
            LOGFILE_CHECKING["LAX"] if jump else LOGFILE_CHECKING["STRICT"]
        )
        self.tomorrow_checking = (
            LOGFILE_CHECKING["LAX"] if jump else LOGFILE_CHECKING["STRICT"]
        )

    @abc.abstractmethod
    def construct(self, location=None):
        raise NotImplementedError

    @abc.abstractmethod
    def advance(self, now=None, simulate=None):
        raise NotImplementedError

    @abc.abstractmethod
    def get_agenda(self, log):
        raise NotImplementedError

    @abc.abstractmethod
    def update_agenda(self, log, agenda):
        raise NotImplementedError

    @abc.abstractmethod
    def save(self):
        raise NotImplementedError
