import datetime
import pytest

from composer.config import LOGFILE_CHECKING
from composer.errors import AgendaNotReviewedError, PlannerIsInTheFutureError
from composer.timeperiod import Zero, Day, Week, Month, Quarter, Year

from mock import MagicMock, patch
from ..fixtures import planner_base


class ReturnTimes(object):

    times = 0

    def __init__(self, n, what, then):
        self.n = n
        self.what = what
        self.then = then

    def __call__(self, *args, **kwargs):
        if self.times < self.n:
            self.times += 1
            return self.what
        return self.then


class TestAdvance(object):
    def _set_up_no_advance(self, planner, current_day, next_day):
        planner.date = current_day
        mock_next_day = MagicMock()
        mock_next_day.return_value = next_day
        planner.next_day = mock_next_day
        mock_advance_period = MagicMock()
        mock_advance_period.return_value = Zero
        planner.advance_period = mock_advance_period

    def _set_up_advance(self, planner, current_day, next_day):
        planner.date = current_day
        mock_next_day = MagicMock()
        mock_next_day.return_value = next_day
        planner.next_day = mock_next_day
        mock_advance_period = MagicMock()
        mock_advance_period.return_value = Day
        planner.advance_period = mock_advance_period

    def test_no_advance_status(self, planner_base):
        current_day = datetime.date(2013, 1, 1)
        next_day = datetime.date(2013, 1, 2)
        self._set_up_no_advance(planner_base, current_day, next_day)
        status, _ = planner_base.advance()
        assert status == Zero

    def test_no_advance_next_planner(self, planner_base):
        current_day = datetime.date(2013, 1, 1)
        next_day = datetime.date(2013, 1, 2)
        self._set_up_no_advance(planner_base, current_day, next_day)
        _, next_day_planner = planner_base.advance()
        assert next_day_planner is None

    def test_advance_status(self, planner_base):
        current_day = datetime.date(2013, 1, 1)
        next_day = datetime.date(2013, 1, 2)
        self._set_up_advance(planner_base, current_day, next_day)
        status, _ = planner_base.advance()
        assert status == Day

    def test_advance_next_planner(self, planner_base):
        current_day = datetime.date(2013, 1, 1)
        next_day = datetime.date(2013, 1, 2)
        self._set_up_advance(planner_base, current_day, next_day)
        _, next_day_planner = planner_base.advance()
        assert next_day_planner.date == next_day

    @patch('composer.backend.base.datetime')
    def test_attempt_to_advance_from_future_raises_error(
        self, mock_datetime, planner_base
    ):
        planner_day = datetime.date(2013, 1, 2)
        today = datetime.date(2013, 1, 1)
        next_day = datetime.date(2013, 1, 2)
        mock_datetime.date.today.return_value = today
        self._set_up_advance(planner_base, planner_day, next_day)
        with pytest.raises(PlannerIsInTheFutureError):
            _, next_day_planner = planner_base.advance()


class TestAdvancePeriod(object):
    def _set_up_advance(self, mock_next_period, planner, n=1):
        current_day = datetime.date(2013, 1, 1)
        planner.date = current_day
        planner.week_theme = ''
        planner.agenda_reviewed = Year
        next_day = datetime.date(2013, 1, 2)
        mock_next_day = MagicMock()
        mock_next_day.return_value = next_day
        planner.next_day = mock_next_day
        mock_get_log = MagicMock()
        mock_get_log.return_value = True
        planner.get_log = mock_get_log
        next_period = (
            Week.__class__()
        )  # patching the singleton directly has global effect
        mock_start_of_period = ReturnTimes(n, True, False)
        next_period.is_start_of_period = mock_start_of_period
        mock_next_period.return_value = next_period

    @patch('composer.backend.base.get_next_period')
    def test_advance_ends_period(self, mock_next_period, planner_base):
        self._set_up_advance(mock_next_period, planner_base)
        planner_base.end_period = MagicMock()
        planner_base.advance_period(Day)
        assert planner_base.end_period.called

    @patch('composer.backend.base.get_next_period')
    def test_advance_begins_period(self, mock_next_period, planner_base):
        self._set_up_advance(mock_next_period, planner_base)
        planner_base.end_period = MagicMock()
        planner_base.begin_period = MagicMock()
        planner_base.advance_period(Day)
        assert planner_base.begin_period.called

    @patch('composer.backend.base.get_next_period')
    def test_advance_attempts_encompassing_period(
        self, mock_next_period, planner_base
    ):
        self._set_up_advance(mock_next_period, planner_base, n=2)
        planner_base.end_period = MagicMock()
        planner_base.begin_period = MagicMock()
        result = planner_base.advance_period(Day)
        assert result == Week

    @patch('composer.backend.base.get_next_period')
    def test_no_advance_continues_period(self, mock_next_period, planner_base):
        self._set_up_advance(mock_next_period, planner_base, n=0)
        planner_base.end_period = MagicMock()
        planner_base.begin_period = MagicMock()
        planner_base.continue_period = MagicMock()
        planner_base.advance_period(Day)
        assert planner_base.continue_period.called

    def _set_up_advance_decision(self, planner, current_day):
        planner.date = current_day
        planner.week_theme = ''
        planner.agenda_reviewed = Year
        mock_get_log = MagicMock()
        mock_get_log.return_value = True
        planner.get_log = mock_get_log
        planner.begin_period = MagicMock()
        planner.end_period = MagicMock()
        planner.continue_period = MagicMock()

    def test_decision_for_typical_day_advance(self, planner_base):
        """ Check that planner advance takes the correct decision to advance
        day on a typical day change boundary
        """
        current_day = datetime.date(2012, 12, 5)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Day

    @patch('composer.backend.base.datetime')
    def test_decision_for_present_day_in_progress_advance(
        self, mock_datetime, planner_base
    ):
        current_day = datetime.date.today()
        hour = 10
        now = datetime.datetime(
            current_day.year, current_day.month, current_day.day, hour
        )
        mock_datetime.datetime.now.return_value = now
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Zero

    @patch('composer.backend.base.datetime')
    def test_decision_for_present_day_eod_advance(
        self, mock_datetime, planner_base
    ):
        current_day = datetime.date.today()
        hour = 18
        now = datetime.datetime(
            current_day.year, current_day.month, current_day.day, hour
        )
        mock_datetime.datetime.now.return_value = now
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Day

    def test_decision_for_first_week_too_short_day_advance(self, planner_base):
        """ Check that planner advance takes the correct decision to advance
        only day when first week is too short
        """
        # 3/3/2012 is a Saturday, but since current week is only 3 days (too
        # short), should advance only day
        current_day = datetime.date(2012, 3, 3)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Day

    def test_decision_for_first_week_borderline_too_short_day_advance(
        self, planner_base
    ):
        """ Check that planner advance takes the correct decision to advance
        only day when first week is just below minimum length
        """
        # 2/4/2012 is a Saturday, but since current week is 4 days (just short
        # of requirement), should advance only day
        current_day = datetime.date(2012, 2, 4)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Day

    def test_decision_for_last_week_too_short_day_advance(self, planner_base):
        """ Check that planner advance takes the correct decision to advance
        only day when last week would be too short
        """
        # 12/29/2012 is a Saturday, but since new week would be too short,
        # should advance only day
        current_day = datetime.date(2012, 12, 29)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Day

    def test_decision_for_last_week_borderline_too_short_day_advance(
        self, planner_base
    ):
        """ Check that planner advance takes the correct decision to advance
        only day when last week would be just below minimum length
        """
        # 2/25/2012 is a Saturday, but since new week is 4 days (just short of
        # requirement), should advance only day
        current_day = datetime.date(2012, 2, 25)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Day

    def test_decision_for_typical_week_advance(self, planner_base):
        """ Check that planner advance takes the correct decision to advance
        week on a typical week change boundary
        """
        current_day = datetime.date(2012, 12, 8)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Week

    def test_decision_for_first_week_borderline_long_enough_week_advance(
        self, planner_base
    ):
        """ Check that planner advance takes the correct decision to advance
        week when last week would be just at minimum length
        """
        # 5/5/2012 is Sat, and current week is exactly 5 days long (long
        # enough), so should advance week
        current_day = datetime.date(2012, 5, 5)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Week

    def test_decision_for_last_week_borderline_long_enough_week_advance(
        self, planner_base
    ):
        """ Check that planner advance takes the correct decision to advance
        week when last week would be just at minimum length
        """
        # 5/26/2012 is Sat, and new week would be exactly 5 days long (long
        # enough), so should advance week
        current_day = datetime.date(2012, 5, 26)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Week

    def test_decision_for_month_advance(self, planner_base):
        """ Check that planner advance takes the correct decision to advance
        month on a month change boundary
        """
        current_day = datetime.date(2012, 11, 30)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Month

    def test_decision_for_quarter_advance(self, planner_base):
        """ Check that planner advance takes the correct decision to advance
        quarter on a quarter change boundary
        """
        current_day = datetime.date(2012, 3, 31)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Quarter

    def test_decision_for_year_advance(self, planner_base):
        """ Check that planner advance takes the correct decision to advance
        year on a year change boundary
        """
        current_day = datetime.date(2012, 12, 31)
        self._set_up_advance_decision(planner_base, current_day)
        status = planner_base.advance_period()
        assert status == Year

    def test_decision_for_jump_in_week(self, planner_base):
        current_day = datetime.date(2012, 11, 13)
        self._set_up_advance_decision(planner_base, current_day)
        planner_base.jump_to_date = datetime.date(2012, 11, 17)
        planner_base.get_log.return_value = True
        status = planner_base.advance_period()
        assert status == Day

    def test_decision_for_jump_outside_week(self, planner_base):
        current_day = datetime.date(2012, 11, 13)
        self._set_up_advance_decision(planner_base, current_day)
        planner_base.jump_to_date = datetime.date(2012, 11, 19)
        planner_base.get_log = ReturnTimes(1, False, True)
        status = planner_base.advance_period()
        assert status == Week

    def test_decision_for_jump_outside_month(self, planner_base):
        current_day = datetime.date(2012, 11, 13)
        self._set_up_advance_decision(planner_base, current_day)
        planner_base.jump_to_date = datetime.date(2012, 12, 19)
        planner_base.get_log = ReturnTimes(2, False, True)
        status = planner_base.advance_period()
        assert status == Month

    def test_decision_for_jump_outside_quarter(self, planner_base):
        current_day = datetime.date(2012, 9, 13)
        self._set_up_advance_decision(planner_base, current_day)
        planner_base.jump_to_date = datetime.date(2012, 10, 19)
        planner_base.get_log = ReturnTimes(3, False, True)
        status = planner_base.advance_period()
        assert status == Quarter

    def test_decision_for_jump_outside_year(self, planner_base):
        current_day = datetime.date(2012, 9, 13)
        self._set_up_advance_decision(planner_base, current_day)
        planner_base.jump_to_date = datetime.date(2013, 10, 19)
        planner_base.get_log = ReturnTimes(4, False, True)
        status = planner_base.advance_period()
        assert status == Year


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
            "jump": False,
            "week_theme": "revival",
            "agenda_reviewed": Week,
        }
        planner.set_preferences(preferences)
        assert planner.schedule == preferences['schedule']
        assert planner.preferred_bullet_char == preferences['bullet_character']
        assert planner.jump_to_date is None
        assert (
            planner.logfile_completion_checking
            == preferences['logfile_completion_checking']
        )
        assert planner.week_theme == preferences.get("week_theme")
        assert planner.agenda_reviewed == preferences.get("agenda_reviewed")

    @patch('composer.backend.base.datetime')
    def test_jump_overrides_strict_checking(self, mock_datetime, planner_base):
        planner = planner_base
        preferences = {
            "schedule": "standard",
            "bullet_character": "*",
            "logfile_completion_checking": LOGFILE_CHECKING['STRICT'],
            "jump": True,
            "week_theme": "revival",
        }
        today = datetime.date.today()
        planner.date = today - datetime.timedelta(days=10)
        mock_datetime.date.today.return_value = today
        planner.set_preferences(preferences)
        assert planner.schedule == preferences['schedule']
        assert planner.preferred_bullet_char == preferences['bullet_character']
        assert planner.jump_to_date == today
        assert planner.logfile_completion_checking == LOGFILE_CHECKING['LAX']
        assert planner.week_theme == preferences.get("week_theme")


class TestJumpDate(object):
    def test_jump_date(self, planner_base):
        planner = planner_base
        jump_to_date = planner.date + datetime.timedelta(days=10)
        planner.set_jump_date(jump_to_date)
        assert planner.jump_to_date == jump_to_date

    def test_date_in_past_is_ignored(self, planner_base):
        planner = planner_base
        jump_to_date = planner.date
        planner.set_jump_date(jump_to_date)
        assert planner.jump_to_date is None
