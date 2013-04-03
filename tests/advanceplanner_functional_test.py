#!/usr/bin/env python

import unittest
import advanceplanner
from advanceplanner import PlannerPeriod
import datetime

class AdvancePlanner(unittest.TestCase):

	def testAdvancePlannerDay(self):
		""" Actually operate on a wiki that's configured such that only a day advance
		is in order. After running the test check that this is what has happened
		(git status / diff if git managed test wikis)
		"""
		WIKIPATH = 'tests/testwikis/daywiki'
		now = datetime.datetime(2012,12,6,19,0,0)
		status = advanceplanner.advanceFilesystemPlanner(WIKIPATH, now)
		self.assertEqual(status, PlannerPeriod.Day)

	def testAdvancePlannerWeek(self):
		""" Actually operate on a wiki that's configured such that a week advance
		is in order. After running the test check that this is what has happened
		(git status / diff if git managed test wikis)
		"""
		WIKIPATH = 'tests/testwikis/weekwiki'
		now = datetime.datetime(2012,12,8,19,0,0)
		status = advanceplanner.advanceFilesystemPlanner(WIKIPATH, now)
		self.assertEqual(status, PlannerPeriod.Week)

	def testAdvancePlannerMonth(self):
		""" Actually operate on a wiki that's configured such that a month advance
		is in order. After running the test check that this is what has happened
		(git status / diff if git managed test wikis)
		"""
		WIKIPATH = 'tests/testwikis/monthwiki'
		now = datetime.datetime(2012,12,31,19,0,0)
		status = advanceplanner.advanceFilesystemPlanner(WIKIPATH, now)
		self.assertEqual(status, PlannerPeriod.Month)
