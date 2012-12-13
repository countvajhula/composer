#!/usr/bin/env python

import unittest
import advanceplanner
from advanceplanner import Planner
from advanceplanner import AdvancePlannerStatus
from StringIO import StringIO
import datetime

class AdvancePlanner(unittest.TestCase):

	def testAdvancePlannerDay(self):
		WIKIPATH = 'tests/testwikis/daywiki'
		now = datetime.datetime(2012,12,6,19,0,0)
		status = advanceplanner.advanceFilesystemPlanner(WIKIPATH, now)
		self.assertEqual(status, AdvancePlannerStatus.DayAdded)

	def testAdvancePlannerWeek(self):
		WIKIPATH = 'tests/testwikis/weekwiki'
		now = datetime.datetime(2012,12,8,19,0,0)
		status = advanceplanner.advanceFilesystemPlanner(WIKIPATH, now)
		self.assertEqual(status, AdvancePlannerStatus.WeekAdded)

	def testAdvancePlannerMonth(self):
		WIKIPATH = 'tests/testwikis/monthwiki'
		now = datetime.datetime(2012,12,31,19,0,0)
		status = advanceplanner.advanceFilesystemPlanner(WIKIPATH, now)
		self.assertEqual(status, AdvancePlannerStatus.MonthAdded)
