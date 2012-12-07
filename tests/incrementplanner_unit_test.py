#!/usr/bin/env python

import unittest
import incrementplanner
from incrementplanner import Planner
from incrementplanner import AdvancePlannerStatus
from StringIO import StringIO
import datetime

""" 
1. add year later
2. improve later to have dif templates for each day -- *day*
3. if attempt to create already exists throw exception
4. add if (themes) condition
5. Check current date and day, get "successor" using python date module (unit tests for this)
"""
class PlannerDateIntegrityTester(unittest.TestCase):
	""" check dates are advanced correctly - edge cases, leap years """
	pass

class PlannerPeriodIntegrityTester(unittest.TestCase):
	"""end of month period, 1st of month"""
	pass

class PlannerFilesystemIntegrityTester(unittest.TestCase):
	""" check exceptions if file exists (e.g. running twice). Check symlinks are updated """
	pass

class PlannerInvalidStateFailGracefullyTester(unittest.TestCase):
	""" check that if any needed files are missing it fails gracefully with exception and without making changes """
	pass

class PlannerAdvanceTester(unittest.TestCase):
	""" Check that planner advances and updates templates correctly """

	monthtemplate = ("= December 2012 =\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	monthadvance_monthtemplate = ("= January 2013 =\n"
					"\n"
					"\t* [[Week of January 1, 2013]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	monthadvance_weektemplate = ("= WEEK OF JANUARY 1, 2013 =\n"
					"\n"
					"Theme: *WEEK OF THEME*\n"
					"\n"
					"\t* [[January 1, 2013]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	default_weekdaytemplate = ("CHECKPOINTS:\n"
					"[ ] 7:00am - wake up []\n[ ] 7:05am - brush + change []\n[ ] 7:10am - protein []\n"
					"[ ] 7:15am - gym []\n[ ] 8:00am - shower []\n[ ] 8:15am - dump []\n"
					"[ ] 11:00pm - (start winding down) brush []\n[ ] 11:05pm - $nasal irrigation$ []\n"
					"[ ] 11:10pm - update schedule []\n[ ] 11:15pm - get stuff ready for morning"
					"((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones"
					") []\n[ ] 11:30pm - sleep []"
					"\n\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule"
					"\n\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	default_weekendtemplate = ("CHECKPOINTS:\n"
					"[ ] 8:00am - wake up []\n[ ] 8:05am - brush + change []\n[ ] 8:10am - protein []\n"
					"[ ] 8:15am - gym []\n[ ] 9:00am - shower []\n[ ] 9:15am - weigh yourself (saturday) []"
					"\n\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule"
					"\n\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	weektemplate = ("= WEEK OF DECEMBER 1, 2012 =\n"
					"\n"
					"Theme: *WEEK OF THEME*\n"
					"\n"
					"\t* [[December 5, 2012]]\n"
					"\t* [[December 4, 2012]]\n"
					"\t* [[December 3, 2012]]\n"
					"\t* [[December 2, 2012]]\n"
					"\t* [[December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	weekadvance_weektemplate = ("= WEEK OF DECEMBER 9, 2012 =\n"
					"\n"
					"Theme: *WEEK OF THEME*\n"
					"\n"
					"\t* [[December 9, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	weekadvance_monthtemplate = ("= December 2012 =\n"
					"\t* [[Week of December 9, 2012]]\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	daytemplate = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"[x] 7:05am - brush + change [11:00]\n"
					"[ ] 7:10am - protein []\n"
					"[ ] 7:15am - gym []\n"
					"[x] 8:00am - shower [11:10]\n"
					"[ ] 11:05pm - $nasal irrigation$ []\n"
					"[x] 11:10pm - update schedule [12:25]\n"
					"[x] 11:15pm - get stuff ready for morning((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones) [8:45]\n"
					"[x] 11:30pm - sleep [12:45]\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"[x] take out trash\n"
					"[x] floss\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"[x] Make bed\n"
					"[x] 5 mins housework (dishes, clearing, folding, trash, ...)\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"Time spent on PLANNER: 15 mins")

	dayadvance_weektemplate = ("= WEEK OF DECEMBER 1, 2012 =\n"
					"\n"
					"Theme: *WEEK OF THEME*\n"
					"\n"
					"\t* [[December 6, 2012]]\n"
					"\t* [[December 5, 2012]]\n"
					"\t* [[December 4, 2012]]\n"
					"\t* [[December 3, 2012]]\n"
					"\t* [[December 2, 2012]]\n"
					"\t* [[December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	checkpoints_month = "[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []"
	checkpoints_week = "[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []"
	checkpoints_weekday = ("[ ] 7:00am - wake up []\n[ ] 7:05am - brush + change []\n[ ] 7:10am - protein []\n"
			"[ ] 7:15am - gym []\n[ ] 8:00am - shower []\n[ ] 8:15am - dump []\n"
			"[ ] 11:00pm - (start winding down) brush []\n[ ] 11:05pm - $nasal irrigation$ []\n"
			"[ ] 11:10pm - update schedule []\n[ ] 11:15pm - get stuff ready for morning"
			"((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones"
			") []\n[ ] 11:30pm - sleep []")
	checkpoints_weekend = ("[ ] 8:00am - wake up []\n[ ] 8:05am - brush + change []\n[ ] 8:10am - protein []\n"
			"[ ] 8:15am - gym []\n[ ] 9:00am - shower []\n[ ] 9:15am - weigh yourself (saturday) []")

	periodic_month = "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials"
	periodic_week = "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick"
	periodic_day = "[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule"

	def setUp(self):
		self.planner = Planner()
		self.planner.date = datetime.date.today()
		self.planner.dayfile = StringIO(self.daytemplate)
		self.planner.weekfile = StringIO(self.weektemplate)
		self.planner.monthfile = StringIO(self.monthtemplate)
		self.planner.checkpoints_month_file = StringIO(self.checkpoints_month)
		self.planner.checkpoints_week_file = StringIO(self.checkpoints_week)
		self.planner.checkpoints_weekday_file = StringIO(self.checkpoints_weekday)
		self.planner.checkpoints_weekend_file = StringIO(self.checkpoints_weekend)
		self.planner.periodic_month_file = StringIO(self.periodic_month)
		self.planner.periodic_week_file = StringIO(self.periodic_week)
		self.planner.periodic_day_file = StringIO(self.periodic_day)

	def testDecisionForTypicalDayAdvance(self):
		""" Check that planner advance takes the correct decision to advance day on a typical day change boundary """
		now = datetime.datetime(2012,12,5,19,0,0)
		self.planner.date = now.date()
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, AdvancePlannerStatus.DayAdded)

	def testDecisionForFirstWeekTooShortDayAdvance(self):
		""" Check that planner advance takes the correct decision to advance only day when first week is too short """
		now = datetime.datetime(2012,3,3,19,0,0) # 3/3/2012 is a Saturday, but since current week is only 3 days (too short), should advance only day
		self.planner.date = now.date()
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, AdvancePlannerStatus.DayAdded)

	def testDecisionForFirstWeekBorderlineTooShortDayAdvance(self):
		""" Check that planner advance takes the correct decision to advance only day when first week is just below minimum length """
		now = datetime.datetime(2012,2,4,19,0,0) # 2/4/2012 is a Saturday, but since current week is 4 days (just short of requirement), should advance only day
		self.planner.date = now.date()
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, AdvancePlannerStatus.DayAdded)

	def testDecisionForLastWeekTooShortDayAdvance(self):
		""" Check that planner advance takes the correct decision to advance only day when last week would be too short """
		now = datetime.datetime(2012,12,29,19,0,0) # 12/29/2012 is a Saturday, but since new week would be too short, should advance only day
		self.planner.date = now.date()
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, AdvancePlannerStatus.DayAdded)

	def testDecisionForLastWeekBorderlineTooShortDayAdvance(self):
		""" Check that planner advance takes the correct decision to advance only day when last week would be just below minimum length """
		now = datetime.datetime(2012,2,25,19,0,0) # 2/25/2012 is a Saturday, but since new week is 4 days (just short of requirement), should advance only day
		self.planner.date = now.date()
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, AdvancePlannerStatus.DayAdded)

	def testDecisionForTypicalWeekAdvance(self):
		""" Check that planner advance takes the correct decision to advance week on a typical week change boundary """
		now = datetime.datetime(2012,12,8,19,0,0)
		self.planner.date = now.date()
		(date, day, month, year) = (self.planner.date.day, self.planner.date.strftime('%A'), self.planner.date.strftime('%B'), self.planner.date.year)
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, AdvancePlannerStatus.WeekAdded)

	def testDecisionForFirstWeekBorderlineLongEnoughWeekAdvance(self):
		""" Check that planner advance takes the correct decision to advance week when last week would be just at minimum length """
		now = datetime.datetime(2012,5,5,19,0,0) # 5/5/2012 is Sat, and current week is exactly 5 days long (long enough), so should advance week
		self.planner.date = now.date()
		(date, day, month, year) = (self.planner.date.day, self.planner.date.strftime('%A'), self.planner.date.strftime('%B'), self.planner.date.year)
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, AdvancePlannerStatus.WeekAdded)

	def testDecisionForLastWeekBorderlineLongEnoughWeekAdvance(self):
		""" Check that planner advance takes the correct decision to advance week when last week would be just at minimum length """
		now = datetime.datetime(2012,5,26,19,0,0) # 5/26/2012 is Sat, and new week would be exactly 5 days long (long enough), so should advance week
		self.planner.date = now.date()
		(date, day, month, year) = (self.planner.date.day, self.planner.date.strftime('%A'), self.planner.date.strftime('%B'), self.planner.date.year)
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, AdvancePlannerStatus.WeekAdded)

	def testDecisionForMonthAdvance(self):
		""" Check that planner advance takes the correct decision to advance month on a month change boundary """
		now = datetime.datetime(2012,11,30,19,0,0)
		self.planner.date = now.date()
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, AdvancePlannerStatus.MonthAdded)

	def testPlannerAdvanceMonth(self):
		""" Check that planner advance returns the correct new month, week, and day templates when advancing month """
		now = datetime.datetime(2012,12,31,19,0,0)
		self.planner.date = now.date()
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(self.planner.monthfile.read(), self.monthadvance_monthtemplate)
		self.assertEqual(self.planner.weekfile.read(), self.monthadvance_weektemplate)
		self.assertEqual(self.planner.dayfile.read(), self.default_weekdaytemplate)

	def testPlannerAdvanceWeek(self):
		""" Check that planner advance returns the correct new week and day templates, and updates the existing month template correctly, when advancing week """
		now = datetime.datetime(2012,12,8,19,0,0)
		self.planner.date = now.date()
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(self.planner.weekfile.read(), self.weekadvance_weektemplate)
		self.assertEqual(self.planner.monthfile.read(), self.weekadvance_monthtemplate)
		self.assertEqual(self.planner.dayfile.read(), self.default_weekendtemplate)

	def testPlannerAdvanceDay(self):
		""" Check that planner advance returns the correct new day template, and updates the existing week template, when advancing day """
		now = datetime.datetime(2012,12,5,19,0,0)
		self.planner.date = now.date()
		status = incrementplanner.advancePlanner(self.planner, now)
		self.assertEqual(self.planner.dayfile.read(), self.default_weekdaytemplate)
		self.assertEqual(self.planner.weekfile.read(), self.dayadvance_weektemplate)

class PlannerNewTemplateIntegrityTester(unittest.TestCase):
	""" Check that new templates generated by the planner are as expected """

	checkpoints_month = "[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []"
	checkpoints_week = "[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []"
	checkpoints_weekday = ("[ ] 7:00am - wake up []\n[ ] 7:05am - brush + change []\n[ ] 7:10am - protein []\n"
			"[ ] 7:15am - gym []\n[ ] 8:00am - shower []\n[ ] 8:15am - dump []\n"
			"[ ] 11:00pm - (start winding down) brush []\n[ ] 11:05pm - $nasal irrigation$ []\n"
			"[ ] 11:10pm - update schedule []\n[ ] 11:15pm - get stuff ready for morning"
			"((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones"
			") []\n[ ] 11:30pm - sleep []")
	checkpoints_weekend = ("[ ] 8:00am - wake up []\n[ ] 8:05am - brush + change []\n[ ] 8:10am - protein []\n"
			"[ ] 8:15am - gym []\n[ ] 9:00am - shower []\n[ ] 9:15am - weigh yourself (saturday) []")

	periodic_month = "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials"
	periodic_week = "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick"
	periodic_day = "[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule"

	def testMonthTemplate(self):
		""" Test that month template is generated correctly by integrating checkpoints, periodic, etc."""
		now = datetime.datetime(2012,12,4,18,50,30)
		today = now.date()
		nextDay = today + datetime.timedelta(days=1)
		checkpointsfile = StringIO(self.checkpoints_month)
		periodicfile = StringIO(self.periodic_month)
		outputfile = StringIO()

		(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
		monthtemplate = "= %s %d =\n" % (month, year)
		monthtemplate += "\n"
		monthtemplate += "\t* [[Week of %s %d, %d]]\n" % (month, date, year)
		monthtemplate += "\n"
		monthtemplate += "CHECKPOINTS:\n"
		monthtemplate += self.checkpoints_month
		monthtemplate += "\n\n"
		monthtemplate += "AGENDA:\n\n"
		monthtemplate += "TODOs:\n\n"
		monthtemplate += "MONTHLYs:\n"
		monthtemplate += self.periodic_month
		monthtemplate += "\n\n"
		monthtemplate += "NOTES:\n\n\n"
		monthtemplate += "Time spent on PLANNER: "

		incrementplanner.writeNewMonthTemplate(nextDay, checkpointsfile, periodicfile, outputfile)

		outputfile.seek(0)
		self.assertEqual(outputfile.read(), monthtemplate)

	def testWeekTemplate(self):
		""" Test that week template is generated correctly by integrating checkpoints, periodic, etc."""
		now = datetime.datetime(2012,12,4,18,50,30)
		today = now.date()
		nextDay = today + datetime.timedelta(days=1)
		checkpointsfile = StringIO(self.checkpoints_week)
		periodicfile = StringIO(self.periodic_week)
		outputfile = StringIO()

		(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
		weektemplate = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
		weektemplate += "\n"
		weektemplate += "Theme: *WEEK OF THEME*\n"
		weektemplate += "\n"
		weektemplate += "\t* [[%s %d, %d]]\n" % (month, date, year)
		weektemplate += "\n"
		weektemplate += "CHECKPOINTS:\n"
		weektemplate += self.checkpoints_week
		weektemplate += "\n\n"
		weektemplate += "AGENDA:\n\n"
		weektemplate += "TODOs:\n\n"
		weektemplate += "WEEKLYs:\n"
		weektemplate += self.periodic_week
		weektemplate += "\n\n"
		weektemplate += "NOTES:\n\n\n"
		weektemplate += "Time spent on PLANNER: "

		incrementplanner.writeNewWeekTemplate(nextDay, checkpointsfile, periodicfile, outputfile)

		outputfile.seek(0)
		self.assertEqual(outputfile.read(), weektemplate)

	def testDailyTemplates(self):
		""" Test that templates for each day are generated correctly by integrating checkpoints, periodic, etc.
		Currently only 2 templates - weekday, and weekend are used. TODO: Add individual templates for each day of the week """
		now = datetime.datetime(2012,12,4,18,50,30)
		def incDate():
			while True:
				newdt = now + datetime.timedelta(days=1)
				yield newdt
		for i in range(7):
			now = incDate().next()
			today = now.date()
			nextDay = today + datetime.timedelta(days=1)
			(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
			if day.lower() in ('saturday', 'sunday'):
				checkpointsfile = StringIO(self.checkpoints_weekend)
			else:
				checkpointsfile = StringIO(self.checkpoints_weekday)
			periodicfile = StringIO(self.periodic_day)
			outputfile = StringIO()

			daytemplate = ""
			daytemplate += "CHECKPOINTS:\n"
			if day.lower() in ('saturday', 'sunday'):
				daytemplate += self.checkpoints_weekend
			else:
				daytemplate += self.checkpoints_weekday
			daytemplate += "\n\n"
			daytemplate += "AGENDA:\n\n"
			daytemplate += "TODOs:\n\n"
			daytemplate += "DAILYs:\n"
			daytemplate += self.periodic_day
			daytemplate += "\n\n"
			daytemplate += "NOTES:\n\n\n"
			daytemplate += "Time spent on PLANNER: "

			incrementplanner.writeNewDayTemplate(nextDay, checkpointsfile, periodicfile, outputfile)

			outputfile.seek(0)
			self.assertEqual(outputfile.read(), daytemplate)

class PlannerExistingTemplateUpdateIntegrityTester(unittest.TestCase):
	""" Check that updates on existing templates modifies the file as expected - does the right thing, does only that thing """

	monthtemplate = ("= December 2012 =\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	monthtemplate_updated = ("= December 2012 =\n"
					"\t* [[Week of December 5, 2012]]\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	weektemplate = ("= WEEK OF DECEMBER 1, 2012 =\n"
					"\n"
					"Theme: *WEEK OF THEME*\n"
					"\n"
					"\t* [[December 4, 2012]]\n"
					"\t* [[December 3, 2012]]\n"
					"\t* [[December 2, 2012]]\n"
					"\t* [[December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	weektemplate_updated = ("= WEEK OF DECEMBER 1, 2012 =\n"
					"\n"
					"Theme: *WEEK OF THEME*\n"
					"\n"
					"\t* [[December 5, 2012]]\n"
					"\t* [[December 4, 2012]]\n"
					"\t* [[December 3, 2012]]\n"
					"\t* [[December 2, 2012]]\n"
					"\t* [[December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"TODOs:\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"Time spent on PLANNER: ")

	def testUpdateExistingMonthTemplate(self):
		""" Check that writing over an existing month template adds the new week, and that there are no other changes """
		now = datetime.datetime(2012,12,4,18,50,30)
		today = now.date()
		nextDay = today + datetime.timedelta(days=1)
		(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
		monthfile = StringIO(self.monthtemplate)
		incrementplanner.writeExistingMonthTemplate(nextDay, monthfile)
		monthfile.seek(0)
		self.assertEqual(monthfile.read(), self.monthtemplate_updated)

	def testUpdateExistingWeekTemplate(self):
		""" Check that writing over an existing week template adds the new day, and that there are no other changes """
		now = datetime.datetime(2012,12,4,18,50,30)
		today = now.date()
		nextDay = today + datetime.timedelta(days=1)
		(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
		weekfile = StringIO(self.weektemplate)
		incrementplanner.writeExistingWeekTemplate(nextDay, weekfile)
		weekfile.seek(0)
		self.assertEqual(weekfile.read(), self.weektemplate_updated)

if __name__ == '__main__':
	unittest.main()
