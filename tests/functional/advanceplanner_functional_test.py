#!/usr/bin/env python

import unittest

from composer.backend import FilesystemPlanner
from composer.timeperiod import (
    Day,
    Week,
    Month,
    Quarter,
    Year,
    get_next_period,
)


class AdvancePlanner(unittest.TestCase):
    def test_advance_planner_day(self):
        """ Actually operate on a wiki that's configured such that only a day
        advance is in order. After running the test check that this is what has
        happened (git status / diff if git managed test wikis)
        """
        WIKIPATH = 'tests/testwikis/daywiki'
        planner = FilesystemPlanner(WIKIPATH)
        status, next_day_planner = planner.advance()
        next_period = get_next_period(status) if status < Year else status
        planner.save(next_period)
        next_day_planner.save(status)
        self.assertEqual(status, Day)

    def test_advance_planner_week(self):
        """ Actually operate on a wiki that's configured such that a week
        advance is in order. After running the test check that this is what has
        happened (git status / diff if git managed test wikis)
        """
        WIKIPATH = 'tests/testwikis/weekwiki'
        planner = FilesystemPlanner(WIKIPATH)
        preferences = {'week_theme': ''}
        planner.set_preferences(preferences)
        status, next_day_planner = planner.advance()
        next_period = get_next_period(status) if status < Year else status
        planner.save(next_period)
        next_day_planner.save(status)
        self.assertEqual(status, Week)

    def test_advance_planner_month(self):
        """ Actually operate on a wiki that's configured such that a month
        advance is in order. After running the test check that this is what has
        happened (git status / diff if git managed test wikis)
        """
        WIKIPATH = 'tests/testwikis/monthwiki'
        planner = FilesystemPlanner(WIKIPATH)
        preferences = {'week_theme': ''}
        planner.set_preferences(preferences)
        status, next_day_planner = planner.advance()
        next_period = get_next_period(status) if status < Year else status
        planner.save(next_period)
        next_day_planner.save(status)
        self.assertEqual(status, Month)

    def test_advance_planner_quarter(self):
        """ Actually operate on a wiki that's configured such that a quarter
        advance is in order. After running the test check that this is what has
        happened (git status / diff if git managed test wikis)
        """
        WIKIPATH = 'tests/testwikis/quarterwiki'
        planner = FilesystemPlanner(WIKIPATH)
        preferences = {'week_theme': ''}
        planner.set_preferences(preferences)
        status, next_day_planner = planner.advance()
        next_period = get_next_period(status) if status < Year else status
        planner.save(next_period)
        next_day_planner.save(status)
        self.assertEqual(status, Quarter)

    def test_advance_planner_year(self):
        """ Actually operate on a wiki that's configured such that a year
        advance is in order. After running the test check that this is what has
        happened (git status / diff if git managed test wikis)
        """
        WIKIPATH = 'tests/testwikis/yearwiki'
        planner = FilesystemPlanner(WIKIPATH)
        preferences = {'week_theme': ''}
        planner.set_preferences(preferences)
        status, next_day_planner = planner.advance()
        next_period = get_next_period(status) if status < Year else status
        planner.save(next_period)
        next_day_planner.save(status)
        self.assertEqual(status, Year)
