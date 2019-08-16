import pytest

try:  # py3
    from unittest.mock import MagicMock
except ImportError:  # py2
    from mock import MagicMock

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO

from composer.config import (
    DEFAULT_BULLET_CHARACTER,
    DEFAULT_SCHEDULE,
    LOGFILE_CHECKING,
)


class PlannerMock(MagicMock):
    """ This is needed because of the semantics of accessing and mutating
    files on the Planner, which only allows mutation via a setter, rather
    than by manually mutating the retrieved file (which will be a copy
    rather than the original). If we used a normal Mock for testing this,
    any manual mutation would reflect on the mock object whereas it wouldn't
    on an actual Planner instance, and tests may pass or fail incorrectly
    on this basis.
    """

    date = None
    tomorrow_checking = LOGFILE_CHECKING['STRICT']
    logfile_completion_checking = LOGFILE_CHECKING['STRICT']
    preferred_bullet_char = DEFAULT_BULLET_CHARACTER
    schedule = DEFAULT_SCHEDULE
    week_theme = None

    _tasklistfile = None
    _daythemesfile = None
    _dayfile = None
    _weekfile = None
    _monthfile = None
    _quarterfile = None
    _yearfile = None
    _checkpoints_weekday_file = None
    _checkpoints_weekend_file = None
    _checkpoints_week_file = None
    _checkpoints_month_file = None
    _checkpoints_quarter_file = None
    _checkpoints_year_file = None
    _periodic_day_file = None
    _periodic_week_file = None
    _periodic_month_file = None
    _periodic_quarter_file = None
    _periodic_year_file = None

    @property
    def tasklistfile(self):
        return StringIO(self._tasklistfile.getvalue())

    @tasklistfile.setter
    def tasklistfile(self, value):
        self._tasklistfile = value

    @property
    def daythemesfile(self):
        return StringIO(self._daythemesfile.getvalue())

    @daythemesfile.setter
    def daythemesfile(self, value):
        self._daythemesfile = value

    @property
    def dayfile(self):
        return StringIO(self._dayfile.getvalue())

    @dayfile.setter
    def dayfile(self, value):
        self._dayfile = value

    @property
    def weekfile(self):
        return StringIO(self._weekfile.getvalue())

    @weekfile.setter
    def weekfile(self, value):
        self._weekfile = value

    @property
    def monthfile(self):
        return StringIO(self._monthfile.getvalue())

    @monthfile.setter
    def monthfile(self, value):
        self._monthfile = value

    @property
    def quarterfile(self):
        return StringIO(self._quarterfile.getvalue())

    @quarterfile.setter
    def quarterfile(self, value):
        self._quarterfile = value

    @property
    def yearfile(self):
        return StringIO(self._yearfile.getvalue())

    @yearfile.setter
    def yearfile(self, value):
        self._yearfile = value


def _logfile():
    contents = ("[ ] a task\n"
                "[\\] a WIP task\n"
                "Just some additional clarifications\n"
                "\n"
                "[o] a scheduled task [$TOMORROW$]\n"
                "[ ] a task with subtasks\n"
                "\t[ ] first thing\n"
                "\tclarification of first thing\n"
                "\t[ ] second thing\n"
                "[ ] another task\n")
    return StringIO(contents)


def _empty_logfile():
    return StringIO("")


def _tasklistfile():
    contents = ("TOMORROW:\n"
                "[ ] a task\n"
                "[\\] a WIP task\n"
                "Just some additional clarifications\n"
                "\n"
                "[o] a scheduled task [$TOMORROW$]\n"
                "THIS WEEK:\n"
                "[ ] a task with subtasks\n"
                "\t[ ] first thing\n"
                "\tclarification of first thing\n"
                "\t[ ] second thing\n"
                "THIS MONTH:\n"
                "\n"
                "UNSCHEDULED:\n"
                "[ ] another task\n")
    return StringIO(contents)


@pytest.fixture
def logfile():
    return _logfile()


@pytest.fixture
def empty_logfile():
    return _empty_logfile()


@pytest.fixture
def tasklist_file():
    return _tasklistfile()
