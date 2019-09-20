import pytest

from composer.backend.filesystem.primitives.files import make_file
from composer.config import LOGFILE_CHECKING
from composer.errors import LogfileAlreadyExistsError, LogfileLayoutError
from composer.backend.filesystem.base import (
    PLANNERTASKLISTFILE,
)
from composer.timeperiod import Zero, Day, Month, Week
from composer.timeperiod.interface import TIME_PERIODS

from mock import MagicMock, patch
from .fixtures import planner, logfile, complete_logfile


class TestGetAgenda(object):
    def test_no_period_returns_none(self, planner):
        result = planner.get_agenda(Zero)
        assert result is None

    def test_missing_agenda_raises_error(self, planner):
        mock_get_logfile = MagicMock()
        mock_get_logfile.return_value = make_file(
            "[ ] a task\n[\\] another task"
        )
        planner._get_logfile = mock_get_logfile
        with pytest.raises(LogfileLayoutError):
            planner.get_agenda(Day)

    def test_get_agenda(self, planner, logfile):
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
        mock_get_logfile.return_value = make_file(
            "[ ] a task\n[\\] another task"
        )
        planner._get_logfile = mock_get_logfile
        with pytest.raises(LogfileLayoutError):
            planner.update_agenda(Day, "[ ] new task\n")

    def test_update_agenda(self, planner, logfile):
        mock_get_logfile = MagicMock()
        mock_get_logfile.return_value = logfile
        planner._get_logfile = mock_get_logfile
        updates = "[ ] new task\n"
        expected = (
            (
                "AGENDA:\n"
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
            + updates
            + ("\n" "NOTES:\n")
        )
        planner.update_agenda(Day, updates)
        assert planner.dayfile.getvalue() == expected


class TestCheckLogCompletion(object):
    def test_lax_checking(self, planner, logfile):
        planner.logfile_completion_checking = LOGFILE_CHECKING['LAX']
        planner.dayfile = logfile
        result = planner.check_log_completion(Day)
        assert result is True

    def test_strict_checking(self, planner, logfile):
        planner.logfile_completion_checking = LOGFILE_CHECKING['STRICT']
        planner.dayfile = logfile
        result = planner.check_log_completion(Day)
        assert result is False

    def test_complete_logfile(self, planner, complete_logfile):
        planner.logfile_completion_checking = LOGFILE_CHECKING['STRICT']
        planner.dayfile = complete_logfile
        result = planner.check_log_completion(Day)
        assert result is True


class TestSave(object):
    @patch(
        'composer.backend.filesystem.base.os.path.isfile', return_value=True
    )
    def test_new_logfile_preexists_raises_error(self, mock_isfile, planner):
        with pytest.raises(LogfileAlreadyExistsError):
            planner.save()

    def _note_filename(self):
        self.filenames = []

        def make_note(contents, filename):
            name_index = filename.rfind('/')
            name = filename[name_index + 1 :]
            self.filenames.append(name)

        return make_note

    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_writes_log_for_all_periods(
        self, mock_write_file, mock_os, planner
    ):
        mock_os.path.isfile.return_value = False
        planner.save()
        expected_files_written = (
            len(TIME_PERIODS)  # all tracked time periods
            - 1  # exclude Zero period
            + 1  # tasklist
        )
        assert mock_write_file.call_count == expected_files_written

    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_writes_log_for_period(self, mock_write_file, mock_os, planner):
        mock_os.path.isfile.return_value = False
        mock_write_file.side_effect = self._note_filename()
        planner.save(Month)
        assert any('Month' in filename for filename in self.filenames)

    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_writes_log_for_contained_period(
        self, mock_write_file, mock_os, planner
    ):
        mock_os.path.isfile.return_value = False
        mock_write_file.side_effect = self._note_filename()
        planner.save(Month)
        assert any('Week' in filename for filename in self.filenames)

    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_writes_log_for_encompassing_period(
        self, mock_write_file, mock_os, planner
    ):
        mock_os.path.isfile.return_value = False
        mock_write_file.side_effect = self._note_filename()
        planner.save(Week)
        assert any(
            'Month' in filename for filename in self.filenames
        )

    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_does_not_write_log_for_unaffected_period(
        self, mock_write_file, mock_os, planner
    ):
        mock_os.path.isfile.return_value = False
        mock_write_file.side_effect = self._note_filename()
        planner.save(Day)
        # because os is mocked, this filename remains 'currentquarter'
        assert not any(
            'Month' in filename for filename in self.filenames
        )

    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_writes_tasklist(self, mock_write_file, mock_os, planner):
        mock_os.path.isfile.return_value = False
        mock_write_file.side_effect = self._note_filename()
        planner.save(Week)
        assert any(
            PLANNERTASKLISTFILE in filename for filename in self.filenames
        )
