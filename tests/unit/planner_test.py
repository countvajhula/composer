import datetime
import pytest

from composer.config import LOGFILE_CHECKING
from composer.timeperiod import Zero, Day, Week, Month, Quarter, Year

from mock import MagicMock, patch
from .fixtures import planner_base


class TestAdvance(object):

    @patch('composer.backend.base.get_next_day')
    def test_no_advance(self, mock_next_day, planner_base):
        current_day = datetime.date(2013, 1, 1)
        planner_base.date = current_day
        next_day = datetime.date(2013, 1, 2)
        mock_next_day.return_value = next_day
        mock_advance_period = MagicMock()
        mock_advance_period.return_value = Zero
        planner_base.advance_period = mock_advance_period
        planner_base.advance()
        assert planner_base.date == current_day

    @patch('composer.backend.base.get_next_day')
    def test_advance(self, mock_next_day, planner_base):
        current_day = datetime.date(2013, 1, 1)
        planner_base.date = current_day
        next_day = datetime.date(2013, 1, 2)
        mock_next_day.return_value = next_day
        mock_advance_period = MagicMock()
        mock_advance_period.return_value = Day
        planner_base.advance_period = mock_advance_period
        planner_base.advance()
        assert planner_base.date == next_day


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
        assert planner.logfile_completion_checking == preferences['logfile_completion_checking']
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
