import datetime
import pytest

from datetime import timedelta

from composer.backend.filesystem.primitives.files import make_file
from composer.config import LOGFILE_CHECKING
from composer.errors import LogfileAlreadyExistsError, LogfileLayoutError
from composer.backend.filesystem.base import PLANNERTASKLISTFILE
from composer.timeperiod import Zero, Day, Month, Week, Quarter, Year, Eternity
from composer.timeperiod.interface import TIME_PERIODS
from composer.backend.filesystem.scheduling import date_to_string

from mock import MagicMock, patch
from ...fixtures import planner, logfile, complete_logfile, tasklist


class TestFilesystemBase(object):
    def note_filename(self):
        self.filenames = []

        def make_note(contents, filename):
            name_index = filename.rfind('/')
            name = filename[name_index + 1 :]
            self.filenames.append(name)

        return make_note


class TestPlanner(TestFilesystemBase):
    pass


class TestGetAgenda(TestPlanner):
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
            "[x] a done task\n"
            "\t[x] with\n"
            "\t[x] subtasks\n"
            "[ ] another task\n"
            "[x] also a done task\n"
            "[-] an invalid task\n"
        )
        result = planner.get_agenda(Day)
        assert result == expected

    def test_get_agenda_completed_only(self, planner, logfile):
        mock_get_logfile = MagicMock()
        mock_get_logfile.return_value = logfile
        planner._get_logfile = mock_get_logfile
        expected = (
            "[o] a scheduled task [$TOMORROW$]\n"
            "[x] a done task\n"
            "\t[x] with\n"
            "\t[x] subtasks\n"
            "[x] also a done task\n"
            "[-] an invalid task\n"
        )
        result = planner.get_agenda(Day, complete=True)
        assert result == expected

    def test_get_agenda_not_completed_only(self, planner, logfile):
        mock_get_logfile = MagicMock()
        mock_get_logfile.return_value = logfile
        planner._get_logfile = mock_get_logfile
        expected = (
            "[ ] a task\n"
            "[\\] a WIP task\n"
            "Just some additional clarifications\n"
            "[ ] a task with subtasks\n"
            "\t[ ] first thing\n"
            "\tclarification of first thing\n"
            "\t[ ] second thing\n"
            "[ ] another task\n"
        )
        result = planner.get_agenda(Day, complete=False)
        assert result == expected


class TestUpdateAgenda(TestPlanner):
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
                "[x] a done task\n"
                "\t[x] with\n"
                "\t[x] subtasks\n"
                "[ ] another task\n"
                "[x] also a done task\n"
                "[-] an invalid task\n"
            )
            + updates
            + ("\n" "NOTES:\n")
        )
        planner.update_agenda(Day, updates)
        assert planner.dayfile.getvalue() == expected


class TestCheckLogCompletion(TestPlanner):
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


class TestOkToAdvance(TestPlanner):
    @patch(
        'composer.backend.filesystem.interface.os.path.isfile',
        return_value=True,
    )
    def test_new_logfile_preexists_raises_error(self, mock_isfile, planner):
        with pytest.raises(LogfileAlreadyExistsError):
            planner.is_ok_to_advance()


class TestPlannerSave(TestPlanner):
    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_writes_log_for_all_periods(
        self, mock_write_file, mock_os, planner
    ):
        planner.save()
        expected_files_written = (
            len(TIME_PERIODS)  # all tracked time periods
            - 2  # exclude Zero and Eternity periods
        )
        assert mock_write_file.call_count == expected_files_written

    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_writes_log_for_period(self, mock_write_file, mock_os, planner):
        mock_write_file.side_effect = self.note_filename()
        planner.save(Month)
        assert any('Month' in filename for filename in self.filenames)

    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_writes_log_for_contained_period(
        self, mock_write_file, mock_os, planner
    ):
        mock_write_file.side_effect = self.note_filename()
        planner.save(Month)
        assert any('Week' in filename for filename in self.filenames)

    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_does_not_write_log_for_unaffected_period(
        self, mock_write_file, mock_os, planner
    ):
        mock_write_file.side_effect = self.note_filename()
        planner.save(Day)
        # because os is mocked, this filename remains 'currentquarter'
        assert not any('Month' in filename for filename in self.filenames)


class TestTasklist(TestFilesystemBase):
    def _tasklist(self, task="", period=Day):
        contents = (
            (
                "TOMORROW:\n"
                "[ ] a task\n"
                "Just some additional clarifications\n"
                "\n"
                "[\\] a WIP task\n"
            )
            + (task if period == Day else "")
            + (
                "THIS WEEK:\n"
                "[ ] a task with subtasks\n"
                "\t[\\] first thing\n"
                "\tclarification of first thing\n"
                "\t[ ] second thing\n"
            )
            + (task if period == Week else "")
            + ("THIS MONTH:\n")
            + (task if period == Month else "")
            + ("THIS QUARTER:\n")
            + (task if period == Quarter else "")
            + ("THIS YEAR:\n")
            + (task if period == Year else "")
            + ("UNSCHEDULED:\n" "[ ] another task\n")
            + (task if period == Eternity else "")
        )
        return contents


class TestTasklistSave(TestTasklist):
    @patch('composer.backend.filesystem.base.os')
    @patch('composer.backend.filesystem.base.write_file')
    def test_writes_tasklist(self, mock_write_file, mock_os, tasklist):
        mock_write_file.side_effect = self.note_filename()
        tasklist.save()
        assert any(
            PLANNERTASKLISTFILE in filename for filename in self.filenames
        )


class TestTasklistPlaceTasks(TestTasklist):
    def test_tomorrow(self, tasklist):
        today = datetime.date(2013, 2, 14)
        original = self._tasklist()
        tasklist.file = make_file(original)
        task = "[o] something [$FEBRUARY 14, 2013$]\n"
        expected = self._tasklist(task, Day)
        tasklist.place_tasks([task], today)
        assert tasklist.file.getvalue() == expected

    def test_past_due_placed_in_tomorrow(self, tasklist):
        today = datetime.date(2013, 2, 14)
        original = self._tasklist()
        tasklist.file = make_file(original)
        task = "[o] something [$FEBRUARY 12, 2013$]\n"
        expected = self._tasklist(task, Day)
        tasklist.place_tasks([task], today)
        assert tasklist.file.getvalue() == expected

    def test_this_week(self, tasklist):
        today = datetime.date(2013, 2, 14)
        original = self._tasklist()
        tasklist.file = make_file(original)
        task = "[o] something [$FEBRUARY 16, 2013$]\n"
        expected = self._tasklist(task, Week)
        tasklist.place_tasks([task], today)
        assert tasklist.file.getvalue() == expected

    def test_this_month(self, tasklist):
        today = datetime.date(2013, 2, 14)
        original = self._tasklist()
        tasklist.file = make_file(original)
        task = "[o] something [$FEBRUARY 18, 2013$]\n"
        expected = self._tasklist(task, Month)
        tasklist.place_tasks([task], today)
        assert tasklist.file.getvalue() == expected

    def test_this_quarter(self, tasklist):
        today = datetime.date(2013, 2, 14)
        original = self._tasklist()
        tasklist.file = make_file(original)
        task = "[o] something [$MARCH 18, 2013$]\n"
        expected = self._tasklist(task, Quarter)
        tasklist.place_tasks([task], today)
        assert tasklist.file.getvalue() == expected

    def test_this_year(self, tasklist):
        today = datetime.date(2013, 2, 14)
        original = self._tasklist()
        tasklist.file = make_file(original)
        task = "[o] something [$JULY 18, 2013$]\n"
        expected = self._tasklist(task, Year)
        tasklist.place_tasks([task], today)
        assert tasklist.file.getvalue() == expected

    def test_later(self, tasklist):
        today = datetime.date(2013, 2, 14)
        original = self._tasklist()
        tasklist.file = make_file(original)
        task = "[o] something [$JULY 18, 2014$]\n"
        expected = self._tasklist(task, Eternity)
        tasklist.place_tasks([task], today)
        assert tasklist.file.getvalue() == expected


class TestStandardizeEntries(TestTasklist):
    def test_standardize_entries(self, tasklist):
        today = datetime.date(2013, 2, 14)
        task = "[o] something [$FEBRUARY 16$]\n"
        original = self._tasklist(task, Week)
        tasklist.file = make_file(original)
        standardized_task = "[o] something [$FEBRUARY 16, 2013$]\n"
        expected = self._tasklist(standardized_task, Week)
        tasklist.standardize_entries(today)
        assert tasklist.file.getvalue() == expected

    def test_tomorrow(self, tasklist):
        today = datetime.date(2013, 2, 14)
        task = "[o] something [$TOMORROW$]\n"
        original = self._tasklist(task, Day)
        tasklist.file = make_file(original)
        standardized_task = "[o] something [$FEBRUARY 15, 2013$]\n"
        expected = self._tasklist(standardized_task, Day)
        tasklist.standardize_entries(today)
        assert tasklist.file.getvalue() == expected


class TestTasklistAdvance(TestTasklist):
    def _calendar_tasklist(self):
        contents = (
            "TOMORROW:\n"
            "THIS WEEK:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do this week [$FEBRUARY 16, 2013$]\n"
            "THIS MONTH:\n"
            "[o] do this month [$FEBRUARY 28, 2013$]\n"
            "THIS QUARTER:\n"
            "[o] do this quarter [$MARCH 11, 2013$]\n"
            "THIS YEAR:\n"
            "[o] do this year [$MAY 29, 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do later [$JULY 12, 2014$]\n"
        )
        return contents

    def _canonical_tasklist(self):
        contents = (
            "TOMORROW:\n"
            "THIS WEEK:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "THIS MONTH:\n"
            "[o] do next week [$WEEK OF FEBRUARY 17, 2013$]\n"
            "THIS QUARTER:\n"
            "[o] do next month [$MARCH 2013$]\n"
            "THIS YEAR:\n"
            "[o] do next quarter [$Q2 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do next year [$2014$]\n"
            "[o] do later [$2015$]\n"
        )
        return contents

    def test_advance_by_day(self, tasklist):
        tomorrow = datetime.date(2013, 2, 12)
        original = self._calendar_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "THIS WEEK:\n"
            "[o] do this week [$FEBRUARY 16, 2013$]\n"
            "THIS MONTH:\n"
            "[o] do this month [$FEBRUARY 28, 2013$]\n"
            "THIS QUARTER:\n"
            "[o] do this quarter [$MARCH 11, 2013$]\n"
            "THIS YEAR:\n"
            "[o] do this year [$MAY 29, 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do later [$JULY 12, 2014$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_advance_to_eow(self, tasklist):
        tomorrow = datetime.date(2013, 2, 16)
        original = self._calendar_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do this week [$FEBRUARY 16, 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "[o] do this month [$FEBRUARY 28, 2013$]\n"
            "THIS QUARTER:\n"
            "[o] do this quarter [$MARCH 11, 2013$]\n"
            "THIS YEAR:\n"
            "[o] do this year [$MAY 29, 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do later [$JULY 12, 2014$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_advance_by_week(self, tasklist):
        tomorrow = datetime.date(2013, 2, 24)
        original = self._calendar_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do this week [$FEBRUARY 16, 2013$]\n"
            "THIS WEEK:\n"
            "[o] do this month [$FEBRUARY 28, 2013$]\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "[o] do this quarter [$MARCH 11, 2013$]\n"
            "THIS YEAR:\n"
            "[o] do this year [$MAY 29, 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do later [$JULY 12, 2014$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_advance_to_eom(self, tasklist):
        tomorrow = datetime.date(2013, 2, 28)
        original = self._calendar_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do this week [$FEBRUARY 16, 2013$]\n"
            "[o] do this month [$FEBRUARY 28, 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "[o] do this quarter [$MARCH 11, 2013$]\n"
            "THIS YEAR:\n"
            "[o] do this year [$MAY 29, 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do later [$JULY 12, 2014$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_advance_by_month(self, tasklist):
        tomorrow = datetime.date(2013, 3, 1)
        original = self._calendar_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do this week [$FEBRUARY 16, 2013$]\n"
            "[o] do this month [$FEBRUARY 28, 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "[o] do this quarter [$MARCH 11, 2013$]\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "[o] do this year [$MAY 29, 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do later [$JULY 12, 2014$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_advance_to_eoq(self, tasklist):
        tomorrow = datetime.date(2013, 3, 31)
        original = self._calendar_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do this week [$FEBRUARY 16, 2013$]\n"
            "[o] do this month [$FEBRUARY 28, 2013$]\n"
            "[o] do this quarter [$MARCH 11, 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "[o] do this year [$MAY 29, 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do later [$JULY 12, 2014$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_advance_by_quarter(self, tasklist):
        tomorrow = datetime.date(2013, 4, 1)
        original = self._calendar_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do this week [$FEBRUARY 16, 2013$]\n"
            "[o] do this month [$FEBRUARY 28, 2013$]\n"
            "[o] do this quarter [$MARCH 11, 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "[o] do this year [$MAY 29, 2013$]\n"
            "THIS YEAR:\n"
            "UNSCHEDULED:\n"
            "[o] do later [$JULY 12, 2014$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_advance_to_eoy(self, tasklist):
        tomorrow = datetime.date(2013, 12, 31)
        original = self._calendar_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do this week [$FEBRUARY 16, 2013$]\n"
            "[o] do this month [$FEBRUARY 28, 2013$]\n"
            "[o] do this quarter [$MARCH 11, 2013$]\n"
            "[o] do this year [$MAY 29, 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "UNSCHEDULED:\n"
            "[o] do later [$JULY 12, 2014$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_advance_by_year(self, tasklist):
        tomorrow = datetime.date(2014, 1, 1)
        original = self._calendar_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do this week [$FEBRUARY 16, 2013$]\n"
            "[o] do this month [$FEBRUARY 28, 2013$]\n"
            "[o] do this quarter [$MARCH 11, 2013$]\n"
            "[o] do this year [$MAY 29, 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "[o] do later [$JULY 12, 2014$]\n"
            "UNSCHEDULED:\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_tomorrow_to_week(self, tasklist):
        task = "[o] something [$FEBRUARY 15, 2013$]\n"
        original = self._tasklist(task, Day)
        tasklist.file = make_file(original)
        today = datetime.date(2013, 2, 13)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Week)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_tomorrow_to_month(self, tasklist):
        today = datetime.date(2013, 2, 14)
        task = "[o] something [$FEBRUARY 15, 2013$]\n"
        original = self._tasklist(task, Day)
        tasklist.file = make_file(original)
        today = datetime.date(2013, 2, 1)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Month)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_tomorrow_to_quarter(self, tasklist):
        task = "[o] something [$FEBRUARY 15, 2013$]\n"
        original = self._tasklist(task, Day)
        tasklist.file = make_file(original)
        today = datetime.date(2013, 1, 1)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Quarter)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_tomorrow_to_year(self, tasklist):
        task = "[o] something [$JULY 15, 2013$]\n"
        original = self._tasklist(task, Day)
        tasklist.file = make_file(original)
        today = datetime.date(2013, 2, 1)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Year)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_tomorrow_to_later(self, tasklist):
        task = "[o] something [$FEBRUARY 15, 2013$]\n"
        original = self._tasklist(task, Day)
        tasklist.file = make_file(original)
        today = datetime.date(2012, 12, 1)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Eternity)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_week_to_month(self, tasklist):
        task = "[o] something [$FEBRUARY 26, 2013$]\n"
        original = self._tasklist(task, Week)
        tasklist.file = make_file(original)
        today = datetime.date(2013, 2, 14)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Month)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_week_to_quarter(self, tasklist):
        task = "[o] something [$MARCH 26, 2013$]\n"
        original = self._tasklist(task, Week)
        tasklist.file = make_file(original)
        today = datetime.date(2013, 2, 14)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Quarter)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_week_to_year(self, tasklist):
        task = "[o] something [$JULY 26, 2013$]\n"
        original = self._tasklist(task, Week)
        tasklist.file = make_file(original)
        today = datetime.date(2013, 2, 14)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Year)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_week_to_later(self, tasklist):
        task = "[o] something [$FEBRUARY 26, 2013$]\n"
        original = self._tasklist(task, Week)
        tasklist.file = make_file(original)
        today = datetime.date(2012, 12, 1)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Eternity)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_month_to_quarter(self, tasklist):
        task = "[o] something [$MARCH 26, 2013$]\n"
        original = self._tasklist(task, Month)
        tasklist.file = make_file(original)
        today = datetime.date(2013, 2, 14)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Quarter)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_month_to_year(self, tasklist):
        task = "[o] something [$JULY 26, 2013$]\n"
        original = self._tasklist(task, Month)
        tasklist.file = make_file(original)
        today = datetime.date(2013, 2, 14)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Year)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_month_to_later(self, tasklist):
        task = "[o] something [$JULY 26, 2013$]\n"
        original = self._tasklist(task, Month)
        tasklist.file = make_file(original)
        today = datetime.date(2012, 12, 1)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Eternity)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_quarter_to_year(self, tasklist):
        task = "[o] something [$JULY 26, 2013$]\n"
        original = self._tasklist(task, Quarter)
        tasklist.file = make_file(original)
        today = datetime.date(2013, 2, 14)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Year)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_quarter_to_later(self, tasklist):
        task = "[o] something [$JULY 26, 2013$]\n"
        original = self._tasklist(task, Quarter)
        tasklist.file = make_file(original)
        today = datetime.date(2012, 12, 1)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Eternity)
        assert tasklist.file.getvalue() == expected

    def test_miscategorized_year_to_later(self, tasklist):
        task = "[o] something [$JULY 26, 2013$]\n"
        original = self._tasklist(task, Year)
        tasklist.file = make_file(original)
        today = datetime.date(2012, 12, 1)
        tomorrow = today + timedelta(days=1)
        tasklist.advance(tomorrow)
        expected = self._tasklist(task, Eternity)
        assert tasklist.file.getvalue() == expected

    def test_canonical_day_due_on_day(self, tasklist):
        tomorrow = datetime.date(2013, 2, 12)
        original = self._canonical_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "[o] do next week [$WEEK OF FEBRUARY 17, 2013$]\n"
            "THIS QUARTER:\n"
            "[o] do next month [$MARCH 2013$]\n"
            "THIS YEAR:\n"
            "[o] do next quarter [$Q2 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do next year [$2014$]\n"
            "[o] do later [$2015$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_canonical_week_due_on_first_day(self, tasklist):
        tomorrow = datetime.date(2013, 2, 17)
        original = self._canonical_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do next week [$WEEK OF FEBRUARY 17, 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "[o] do next month [$MARCH 2013$]\n"
            "THIS YEAR:\n"
            "[o] do next quarter [$Q2 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do next year [$2014$]\n"
            "[o] do later [$2015$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_canonical_month_due_on_first_day(self, tasklist):
        tomorrow = datetime.date(2013, 3, 1)
        original = self._canonical_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do next week [$WEEK OF FEBRUARY 17, 2013$]\n"
            "[o] do next month [$MARCH 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "[o] do next quarter [$Q2 2013$]\n"
            "UNSCHEDULED:\n"
            "[o] do next year [$2014$]\n"
            "[o] do later [$2015$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_canonical_quarter_due_on_first_day(self, tasklist):
        tomorrow = datetime.date(2013, 4, 1)
        original = self._canonical_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do next week [$WEEK OF FEBRUARY 17, 2013$]\n"
            "[o] do next month [$MARCH 2013$]\n"
            "[o] do next quarter [$Q2 2013$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "UNSCHEDULED:\n"
            "[o] do next year [$2014$]\n"
            "[o] do later [$2015$]\n"
        )
        assert tasklist.file.getvalue() == expected

    def test_canonical_year_due_on_first_day(self, tasklist):
        tomorrow = datetime.date(2014, 1, 1)
        original = self._canonical_tasklist()
        tasklist.file = make_file(original)
        tasklist.advance(tomorrow)
        expected = (
            "TOMORROW:\n"
            "[o] do tomorrow [$FEBRUARY 12, 2013$]\n"
            "[o] do next week [$WEEK OF FEBRUARY 17, 2013$]\n"
            "[o] do next month [$MARCH 2013$]\n"
            "[o] do next quarter [$Q2 2013$]\n"
            "[o] do next year [$2014$]\n"
            "THIS WEEK:\n"
            "THIS MONTH:\n"
            "THIS QUARTER:\n"
            "THIS YEAR:\n"
            "UNSCHEDULED:\n"
            "[o] do later [$2015$]\n"
        )
        assert tasklist.file.getvalue() == expected
