#!/usr/bin/env python

import unittest
from filesystem import *
from utils import PlannerPeriod
import datetime


class AdvancePlanner(unittest.TestCase):

    def test_advance_planner_day(self):
        """ Actually operate on a wiki that's configured such that only a day advance
        is in order. After running the test check that this is what has happened
        (git status / diff if git managed test wikis)
        """
        WIKIPATH = 'tests/testwikis/daywiki'
        now = datetime.datetime(2012, 12, 6, 19, 0, 0)
        status = advance_filesystem_planner(WIKIPATH, now)
        self.assertEqual(status, PlannerPeriod.Day)

    def test_advance_planner_week(self):
        """ Actually operate on a wiki that's configured such that a week advance
        is in order. After running the test check that this is what has happened
        (git status / diff if git managed test wikis)
        """
        WIKIPATH = 'tests/testwikis/weekwiki'
        now = datetime.datetime(2012, 12, 8, 19, 0, 0)
        status = advance_filesystem_planner(WIKIPATH, now)
        self.assertEqual(status, PlannerPeriod.Week)

    def test_advance_planner_month(self):
        """ Actually operate on a wiki that's configured such that a month advance
        is in order. After running the test check that this is what has happened
        (git status / diff if git managed test wikis)
        """
        WIKIPATH = 'tests/testwikis/monthwiki'
        now = datetime.datetime(2012, 12, 31, 19, 0, 0)
        status = advance_filesystem_planner(WIKIPATH, now)
        self.assertEqual(status, PlannerPeriod.Month)

    def test_advance_planner_quarter(self):
        """ Actually operate on a wiki that's configured such that a quarter advance
        is in order. After running the test check that this is what has happened
        (git status / diff if git managed test wikis)
        """
        WIKIPATH = 'tests/testwikis/quarterwiki'
        now = datetime.datetime(2012, 12, 31, 19, 0, 0)
        status = advance_filesystem_planner(WIKIPATH, now)
        self.assertEqual(status, PlannerPeriod.Quarter)

    def test_advance_planner_year(self):
        """ Actually operate on a wiki that's configured such that a year advance
        is in order. After running the test check that this is what has happened
        (git status / diff if git managed test wikis)
        """
        WIKIPATH = 'tests/testwikis/yearwiki'
        now = datetime.datetime(2012, 12, 31, 19, 0, 0)
        status = advance_filesystem_planner(WIKIPATH, now)
        self.assertEqual(status, PlannerPeriod.Year)
