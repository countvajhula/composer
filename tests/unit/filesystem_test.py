import pytest

from composer.backend.filesystem.utils import make_file
from composer.config import LOGFILE_CHECKING
from composer.errors import LogfileLayoutError
from composer.timeperiod import Zero, Day

from mock import MagicMock, patch
from .fixtures import planner, logfile


class TestGetAgenda(object):
    def test_no_period_returns_none(self, planner):
        result = planner.get_agenda(Zero)
        assert result is None

    def test_missing_agenda_raises_error(self, planner):
        mock_get_logfile = MagicMock()
        mock_get_logfile.return_value = make_file("[ ] a task\n[\\] another task")
        planner._get_logfile = mock_get_logfile
        with pytest.raises(LogfileLayoutError):
            planner.get_agenda(Day)

    def test_normal(self, planner, logfile):
        mock_get_logfile = MagicMock()
        mock_get_logfile.return_value = logfile
        planner._get_logfile = mock_get_logfile
        expected = (
            "[ ] a task\n"
            "[\\] a WIP task\n"
            "Just some additional clarifications\n"
            "\n"
            "[o] a scheduled task [$TOMORROW$]\n"
            "[ ] a task with subtasks\n"
            "\t[ ] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "[ ] another task\n"
        )
        result = planner.get_agenda(Day)
        assert result == expected


class TestUpdateAgenda(object):
    def test_missing_agenda_raises_error(self, planner):
        mock_get_logfile = MagicMock()
        mock_get_logfile.return_value = make_file("[ ] a task\n[\\] another task")
        planner._get_logfile = mock_get_logfile
        with pytest.raises(LogfileLayoutError):
            planner.update_agenda(Day, "[ ] new task\n")

    def test_normal(self, planner, logfile):
        mock_get_logfile = MagicMock()
        mock_get_logfile.return_value = logfile
        planner._get_logfile = mock_get_logfile
        updates = "[ ] new task\n"
        expected = logfile.getvalue() + updates
        planner.update_agenda(Day, updates)
        assert planner.dayfile.getvalue() == expected
