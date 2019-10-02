import datetime
import pytest

from composer.config import LOGFILE_CHECKING
from composer.errors import AgendaNotReviewedError
from composer.timeperiod import Zero, Day, Week, Month, Year

from mock import MagicMock, patch
from ..fixtures import planner_base


class TrueTimes(object):

    times = 0

    def __init__(self, n):
        self.n = n

    def __call__(self, *args, **kwargs):
        if self.times < self.n:
            self.times += 1
            return True
        return False


class TestAdvance(object):
    def _set_up_no_advance(
        self, planner, mock_next_day, current_day, next_day
    ):
        planner.date = current_day
        mock_next_day.return_value = next_day
        mock_advance_period = MagicMock()
        mock_advance_period.return_value = Zero
        planner.advance_period = mock_advance_period

    def _set_up_advance(self, planner, mock_next_day, current_day, next_day):
        planner.date = current_day
        mock_next_day.return_value = next_day
        mock_advance_period = MagicMock()
        mock_advance_period.return_value = Day
        planner.advance_period = mock_advance_period

    @patch('composer.backend.base.get_next_day')
    def test_no_advance_status(self, mock_next_day, planner_base):
        current_day = datetime.date(2013, 1, 1)
        next_day = datetime.date(2013, 1, 2)
        self._set_up_no_advance(
            planner_base, mock_next_day, current_day, next_day
        )
        status, _ = planner_base.advance()
        assert status == Zero

    @patch('composer.backend.base.get_next_day')
    def test_no_advance_next_planner(self, mock_next_day, planner_base):
        current_day = datetime.date(2013, 1, 1)
        next_day = datetime.date(2013, 1, 2)
        self._set_up_no_advance(
            planner_base, mock_next_day, current_day, next_day
        )
        _, next_day_planner = planner_base.advance()
        assert next_day_planner is None

    @patch('composer.backend.base.get_next_day')
    def test_advance_status(self, mock_next_day, planner_base):
        current_day = datetime.date(2013, 1, 1)
        next_day = datetime.date(2013, 1, 2)
        self._set_up_advance(
            planner_base, mock_next_day, current_day, next_day
        )
        status, _ = planner_base.advance()
        assert status == Day

    @patch('composer.backend.base.get_next_day')
    def test_advance_next_planner(self, mock_next_day, planner_base):
        current_day = datetime.date(2013, 1, 1)
        next_day = datetime.date(2013, 1, 2)
        self._set_up_advance(
            planner_base, mock_next_day, current_day, next_day
        )
        _, next_day_planner = planner_base.advance()
        assert next_day_planner.date == next_day


class TestAdvancePeriod(object):
    def _set_up_advance(
        self, mock_next_day, mock_next_period, planner_base, n=1
    ):
        now = datetime.datetime(2013, 1, 1)
        planner_base.now = now
        current_day = now.date()
        planner_base.date = current_day
        planner_base.week_theme = ''
        planner_base.agenda_reviewed = Year
        next_day = datetime.date(2013, 1, 2)
        mock_next_day.return_value = next_day
        next_period = (
            Week.__class__()
        )  # patching the singleton directly has global effect
        mock_criteria_met = TrueTimes(n)
        next_period.advance_criteria_met = mock_criteria_met
        mock_next_period.return_value = next_period

    @patch('composer.backend.base.get_next_period')
    @patch('composer.backend.base.get_next_day')
    def test_advance_ends_period(
        self, mock_next_day, mock_next_period, planner_base
    ):
        self._set_up_advance(mock_next_day, mock_next_period, planner_base)
        planner_base.end_period = MagicMock()
        planner_base.advance_period(Day)
        assert planner_base.end_period.called

    @patch('composer.backend.base.get_next_period')
    @patch('composer.backend.base.get_next_day')
    def test_advance_begins_period(
        self, mock_next_day, mock_next_period, planner_base
    ):
        self._set_up_advance(mock_next_day, mock_next_period, planner_base)
        planner_base.end_period = MagicMock()
        planner_base.begin_period = MagicMock()
        planner_base.advance_period(Day)
        assert planner_base.begin_period.called

    @patch('composer.backend.base.get_next_period')
    @patch('composer.backend.base.get_next_day')
    def test_advance_attempts_encompassing_period(
        self, mock_next_day, mock_next_period, planner_base
    ):
        self._set_up_advance(
            mock_next_day, mock_next_period, planner_base, n=2
        )
        planner_base.end_period = MagicMock()
        planner_base.begin_period = MagicMock()
        result = planner_base.advance_period(Day)
        assert result == Week

    @patch('composer.backend.base.get_next_period')
    @patch('composer.backend.base.get_next_day')
    def test_no_advance_continues_period(
        self, mock_next_day, mock_next_period, planner_base
    ):
        self._set_up_advance(
            mock_next_day, mock_next_period, planner_base, n=0
        )
        planner_base.end_period = MagicMock()
        planner_base.begin_period = MagicMock()
        planner_base.continue_period = MagicMock()
        planner_base.advance_period(Day)
        assert planner_base.continue_period.called


class TestBeginPeriod(object):
    def test_creates_log(self, planner_base):
        next_day = datetime.date(2013, 1, 2)
        planner_base.create_log = MagicMock()
        planner_base.agenda_reviewed = Year
        planner_base.begin_period(Day, next_day)
        assert planner_base.create_log.called

    def test_signals_agenda_review(self, planner_base):
        next_day = datetime.date(2013, 1, 2)
        planner_base.create_log = MagicMock()
        planner_base.tasklist = MagicMock()
        planner_base.tasklist.get_tasks.return_value = (1, 2)  # dummy
        planner_base.agenda_reviewed = Week
        with pytest.raises(AgendaNotReviewedError):
            planner_base.begin_period(Month, next_day)

    def test_waives_agenda_review(self, planner_base):
        next_day = datetime.date(2013, 1, 2)
        planner_base.create_log = MagicMock()
        planner_base.tasklist = MagicMock()
        planner_base.tasklist.get_tasks.return_value = (1, 2)  # dummy
        planner_base.agenda_reviewed = Month
        try:
            planner_base.begin_period(Month, next_day)
        except AgendaNotReviewedError:
            pytest.fail("Agenda review signalled when already reviewed.")


class TestEndPeriod(object):
    def test_checks_log_completion(self, planner_base):
        planner_base.check_log_completion = MagicMock()
        planner_base.end_period(Day)
        assert planner_base.check_log_completion.called

    def test_schedules_tasks(self, planner_base):
        planner_base.check_log_completion = MagicMock()
        planner_base.schedule_tasks = MagicMock()
        planner_base.end_period(Day)
        assert planner_base.schedule_tasks.called

    def test_cascades_agenda(self, planner_base):
        planner_base.check_log_completion = MagicMock()
        planner_base.cascade_agenda = MagicMock()
        planner_base.end_period(Day)
        assert planner_base.cascade_agenda.called


class TestContinuePeriod(object):
    def test_updates_log(self, planner_base):
        next_day = datetime.date(2013, 1, 2)
        planner_base.update_log = MagicMock()
        planner_base.continue_period(Day, next_day)
        assert planner_base.update_log.called


class TestPreferences(object):
    def test_set_preferences(self, planner_base):
        planner = planner_base
        preferences = {
            "schedule": "standard",
            "bullet_character": "*",
            "logfile_completion_checking": LOGFILE_CHECKING['STRICT'],
            "tomorrow_checking": LOGFILE_CHECKING['LAX'],
            "jump": False,
            "week_theme": "revival",
        }
        planner.set_preferences(preferences)
        assert planner.schedule == preferences['schedule']
        assert planner.preferred_bullet_char == preferences['bullet_character']
        assert planner.jumping == preferences['jump']
        assert (
            planner.logfile_completion_checking
            == preferences['logfile_completion_checking']
        )
        assert planner.tomorrow_checking == preferences["tomorrow_checking"]
        assert planner.week_theme == preferences.get("week_theme")

    def test_jump_overrides_strict_checking(self, planner_base):
        planner = planner_base
        preferences = {
            "schedule": "standard",
            "bullet_character": "*",
            "logfile_completion_checking": 1,
            "tomorrow_checking": 2,
            "jump": True,
            "week_theme": "revival",
        }
        planner.set_preferences(preferences)
        assert planner.schedule == preferences['schedule']
        assert planner.preferred_bullet_char == preferences['bullet_character']
        assert planner.jumping == preferences['jump']
        assert planner.logfile_completion_checking == LOGFILE_CHECKING['LAX']
        assert planner.tomorrow_checking == LOGFILE_CHECKING['LAX']
        assert planner.week_theme == preferences.get("week_theme")
