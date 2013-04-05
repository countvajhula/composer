#!/usr/bin/env python

import unittest
import advanceplanner
from advanceplanner import Planner
from advanceplanner import PlannerPeriod
from StringIO import StringIO
import datetime

""" 
1. add year later
2. improve later to have dif templates for each day -- *day*
3. if attempt to create already exists throw exception
4. add if (themes) condition
5. Check current date and day, get "successor" using python date module (unit tests for this)
6. Add tests for different partially-done todos
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

	tasklist = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n")

	yeartemplate = ("= 2012 =\n"
					"\t* [[Q4 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] Q1 - []\n[ ] Q2 - []\n[ ] Q3 - []\n[ ] Q4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"YEARLYs:\n"
					"[ ] 1 significant life achievement\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	yeartemplate_agendaupdated = ("= 2012 =\n"
					"\t* [[Q4 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] Q1 - []\n[ ] Q2 - []\n[ ] Q3 - []\n[ ] Q4 - []\n"
					"\n"
					"AGENDA:\n"
					"[x] take out trash\n"
					"[x] floss\n"
					"\n"
					"YEARLYs:\n"
					"[ ] 1 significant life achievement\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	yearadvance_yeartemplate = ("= 2013 =\n"
					"\n"
					"\t* [[Q1 2013]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] Q1 - []\n[ ] Q2 - []\n[ ] Q3 - []\n[ ] Q4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"YEARLYs:\n"
					"[ ] 1 significant life achievement\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	yearadvance_quartertemplate = ("= Q1 2013 =\n"
					"\n"
					"\t* [[Month of January, 2013]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] MONTH 1 - []\n[ ] MONTH 2 - []\n[ ] MONTH 3 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"QUARTERLYs:\n"
					"[ ] 1 major research achievement\n[ ] 1 major coding achievement\n[ ] 1 unique achievement\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	yearadvance_monthtemplate = ("= January 2013 =\n"
					"\n"
					"\t* [[Week of January 1, 2013]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	yearadvance_weektemplate = ("= WEEK OF JANUARY 1, 2013 =\n"
					"\n"
					"\t* [[January 1, 2013]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	quartertemplate = ("= Q4 2012 =\n"
					"\n"
					"\t* [[Month of October, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] MONTH 1 - []\n[ ] MONTH 2 - []\n[ ] MONTH 3 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"QUARTERLYs:\n"
					"[ ] 1 major research achievement\n[ ] 1 major coding achievement\n[ ] 1 unique achievement\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	quartertemplate_agendaupdated = ("= Q4 2012 =\n"
					"\n"
					"\t* [[Month of October, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] MONTH 1 - []\n[ ] MONTH 2 - []\n[ ] MONTH 3 - []\n"
					"\n"
					"AGENDA:\n"
					"[x] take out trash\n"
					"[x] floss\n"
					"\n"
					"QUARTERLYs:\n"
					"[ ] 1 major research achievement\n[ ] 1 major coding achievement\n[ ] 1 unique achievement\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	quarteradvance_yeartemplate = ("= 2012 =\n"
					"\t* [[Q4 2012]]\n"
					"\t* [[Q3 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] Q1 - []\n[ ] Q2 - []\n[ ] Q3 - []\n[ ] Q4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"YEARLYs:\n"
					"[ ] 1 significant life achievement\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	quarteradvance_quartertemplate = quartertemplate

	quarteradvance_monthtemplate = ("= October 2012 =\n"
					"\n"
					"\t* [[Week of October 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	quarteradvance_weektemplate = ("= WEEK OF OCTOBER 1, 2012 =\n"
					"\n"
					"\t* [[October 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	monthtemplate = ("= December 2012 =\n"
					"\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	monthtemplate_agendaupdated = ("= December 2012 =\n"
					"\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"[x] take out trash\n"
					"[x] floss\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	monthadvance_monthtemplate = monthtemplate

	monthadvance_weektemplate = ("= WEEK OF DECEMBER 1, 2012 =\n"
					"\n"
					"\t* [[December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	default_weekdaytemplate = ("CHECKPOINTS:\n"
					"[ ] 7:00am - wake up []\n[ ] 7:05am - brush + change []\n[ ] 7:10am - protein []\n"
					"[ ] 7:15am - gym []\n[ ] 8:00am - shower []\n[ ] 8:15am - dump []\n"
					"[ ] 11:00pm - (start winding down) brush []\n[ ] 11:05pm - $nasal irrigation$ []\n"
					"[ ] 11:10pm - update schedule []\n[ ] 11:15pm - get stuff ready for morning"
					"((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones"
					") []\n[ ] 11:30pm - sleep []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	default_weekendtemplate = ("CHECKPOINTS:\n"
					"[ ] 8:00am - wake up []\n[ ] 8:05am - brush + change []\n[ ] 8:10am - protein []\n"
					"[ ] 8:15am - gym []\n[ ] 9:00am - shower []\n[ ] 9:15am - weigh yourself (saturday) []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

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
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	weekadvance_weektemplate = ("= WEEK OF DECEMBER 9, 2012 =\n"
					"\n"
					"\t* [[December 9, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	weekadvance_monthtemplate = ("= December 2012 =\n"
					"\n"
					"\t* [[Week of December 9, 2012]]\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	weektemplate_agendaupdated = ("= WEEK OF DECEMBER 1, 2012 =\n"
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
					"[x] take out trash\n"
					"[x] floss\n"
					"\n"
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

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
					"TIME SPENT ON PLANNER: 15 mins")

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
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	checkpoints_year = "[ ] Q1 - []\n[ ] Q2 - []\n[ ] Q3 - []\n[ ] Q4 - []\n"
	checkpoints_quarter = "[ ] MONTH 1 - []\n[ ] MONTH 2 - []\n[ ] MONTH 3 - []\n"
	checkpoints_month = "[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
	checkpoints_week = "[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
	checkpoints_weekday = ("[ ] 7:00am - wake up []\n[ ] 7:05am - brush + change []\n[ ] 7:10am - protein []\n"
			"[ ] 7:15am - gym []\n[ ] 8:00am - shower []\n[ ] 8:15am - dump []\n"
			"[ ] 11:00pm - (start winding down) brush []\n[ ] 11:05pm - $nasal irrigation$ []\n"
			"[ ] 11:10pm - update schedule []\n[ ] 11:15pm - get stuff ready for morning"
			"((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones"
			") []\n[ ] 11:30pm - sleep []\n")
	checkpoints_weekend = ("[ ] 8:00am - wake up []\n[ ] 8:05am - brush + change []\n[ ] 8:10am - protein []\n"
			"[ ] 8:15am - gym []\n[ ] 9:00am - shower []\n[ ] 9:15am - weigh yourself (saturday) []\n")

	periodic_year = "[ ] 1 significant life achievement\n"
	periodic_quarter = "[ ] 1 major research achievement\n[ ] 1 major coding achievement\n[ ] 1 unique achievement\n[ ] update financials\n"
	periodic_month = "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
	periodic_week = "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
	periodic_day = "[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule\n"

	def setUp(self):
		self.planner = Planner()
		self.planner.date = datetime.date.today()
		self.planner.tasklistfile = StringIO(self.tasklist)
		self.planner.dayfile = StringIO(self.daytemplate)
		self.planner.weekfile = StringIO(self.weektemplate)
		self.planner.monthfile = StringIO(self.monthtemplate)
		self.planner.quarterfile = StringIO(self.quartertemplate)
		self.planner.yearfile = StringIO(self.yeartemplate)
		self.planner.checkpoints_year_file = StringIO(self.checkpoints_year)
		self.planner.checkpoints_quarter_file = StringIO(self.checkpoints_quarter)
		self.planner.checkpoints_month_file = StringIO(self.checkpoints_month)
		self.planner.checkpoints_week_file = StringIO(self.checkpoints_week)
		self.planner.checkpoints_weekday_file = StringIO(self.checkpoints_weekday)
		self.planner.checkpoints_weekend_file = StringIO(self.checkpoints_weekend)
		self.planner.periodic_year_file = StringIO(self.periodic_year)
		self.planner.periodic_quarter_file = StringIO(self.periodic_quarter)
		self.planner.periodic_month_file = StringIO(self.periodic_month)
		self.planner.periodic_week_file = StringIO(self.periodic_week)
		self.planner.periodic_day_file = StringIO(self.periodic_day)

	def testDecisionForTypicalDayAdvance(self):
		""" Check that planner advance takes the correct decision to advance day on a typical day change boundary """
		now = datetime.datetime(2012,12,5,19,0,0)
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Day)

	def testDecisionForFirstWeekTooShortDayAdvance(self):
		""" Check that planner advance takes the correct decision to advance only day when first week is too short """
		now = datetime.datetime(2012,3,3,19,0,0) # 3/3/2012 is a Saturday, but since current week is only 3 days (too short), should advance only day
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Day)

	def testDecisionForFirstWeekBorderlineTooShortDayAdvance(self):
		""" Check that planner advance takes the correct decision to advance only day when first week is just below minimum length """
		now = datetime.datetime(2012,2,4,19,0,0) # 2/4/2012 is a Saturday, but since current week is 4 days (just short of requirement), should advance only day
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Day)

	def testDecisionForLastWeekTooShortDayAdvance(self):
		""" Check that planner advance takes the correct decision to advance only day when last week would be too short """
		now = datetime.datetime(2012,12,29,19,0,0) # 12/29/2012 is a Saturday, but since new week would be too short, should advance only day
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Day)

	def testDecisionForLastWeekBorderlineTooShortDayAdvance(self):
		""" Check that planner advance takes the correct decision to advance only day when last week would be just below minimum length """
		now = datetime.datetime(2012,2,25,19,0,0) # 2/25/2012 is a Saturday, but since new week is 4 days (just short of requirement), should advance only day
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Day)

	def testDecisionForTypicalWeekAdvance(self):
		""" Check that planner advance takes the correct decision to advance week on a typical week change boundary """
		now = datetime.datetime(2012,12,8,19,0,0)
		self.planner.date = now.date()
		(date, day, month, year) = (self.planner.date.day, self.planner.date.strftime('%A'), self.planner.date.strftime('%B'), self.planner.date.year)
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Week)

	def testDecisionForFirstWeekBorderlineLongEnoughWeekAdvance(self):
		""" Check that planner advance takes the correct decision to advance week when last week would be just at minimum length """
		now = datetime.datetime(2012,5,5,19,0,0) # 5/5/2012 is Sat, and current week is exactly 5 days long (long enough), so should advance week
		self.planner.date = now.date()
		(date, day, month, year) = (self.planner.date.day, self.planner.date.strftime('%A'), self.planner.date.strftime('%B'), self.planner.date.year)
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Week)

	def testDecisionForLastWeekBorderlineLongEnoughWeekAdvance(self):
		""" Check that planner advance takes the correct decision to advance week when last week would be just at minimum length """
		now = datetime.datetime(2012,5,26,19,0,0) # 5/26/2012 is Sat, and new week would be exactly 5 days long (long enough), so should advance week
		self.planner.date = now.date()
		(date, day, month, year) = (self.planner.date.day, self.planner.date.strftime('%A'), self.planner.date.strftime('%B'), self.planner.date.year)
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Week)

	def testDecisionForMonthAdvance(self):
		""" Check that planner advance takes the correct decision to advance month on a month change boundary """
		now = datetime.datetime(2012,11,30,19,0,0)
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Month)

	def testDecisionForQuarterAdvance(self):
		""" Check that planner advance takes the correct decision to advance quarter on a quarter change boundary """
		now = datetime.datetime(2012,3,31,19,0,0)
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Quarter)

	def testDecisionForYearAdvance(self):
		""" Check that planner advance takes the correct decision to advance year on a year change boundary """
		now = datetime.datetime(2012,12,31,19,0,0)
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(status, PlannerPeriod.Year)

	def testPlannerAdvanceYear(self):
		""" Check that planner advance returns the correct new year, quarter, month, week, and day templates when advancing year """
		now = datetime.datetime(2012,12,31,19,0,0)
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(self.planner.yearfile.read(), self.yearadvance_yeartemplate)
		self.assertEqual(self.planner.quarterfile.read(), self.yearadvance_quartertemplate)
		self.assertEqual(self.planner.monthfile.read(), self.yearadvance_monthtemplate)
		self.assertEqual(self.planner.weekfile.read(), self.yearadvance_weektemplate)
		self.assertEqual(self.planner.dayfile.read(), self.default_weekdaytemplate)

	def testPlannerAdvanceQuarter(self):
		""" Check that planner advance returns the correct new quarter, month, week, and day templates when advancing quarter """
		now = datetime.datetime(2012,9,30,19,0,0)
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(self.planner.quarterfile.read(), self.quarteradvance_quartertemplate)
		self.assertEqual(self.planner.monthfile.read(), self.quarteradvance_monthtemplate)
		self.assertEqual(self.planner.weekfile.read(), self.quarteradvance_weektemplate)
		self.assertEqual(self.planner.dayfile.read(), self.default_weekdaytemplate)

	def testPlannerAdvanceMonth(self):
		""" Check that planner advance returns the correct new month, week, and day templates when advancing month """
		now = datetime.datetime(2012,11,30,19,0,0)
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(self.planner.monthfile.read(), self.monthadvance_monthtemplate)
		self.assertEqual(self.planner.weekfile.read(), self.monthadvance_weektemplate)
		self.assertEqual(self.planner.dayfile.read(), self.default_weekendtemplate)

	def testPlannerAdvanceWeek(self):
		""" Check that planner advance returns the correct new week and day templates, and updates the existing month template correctly, when advancing week """
		now = datetime.datetime(2012,12,8,19,0,0)
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(self.planner.weekfile.read(), self.weekadvance_weektemplate)
		self.assertEqual(self.planner.monthfile.read(), self.weekadvance_monthtemplate)
		self.assertEqual(self.planner.dayfile.read(), self.default_weekendtemplate)

	def testPlannerAdvanceDay(self):
		""" Check that planner advance returns the correct new day template, and updates the existing week template, when advancing day """
		now = datetime.datetime(2012,12,5,19,0,0)
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		status = advanceplanner.advancePlanner(self.planner, now)
		self.assertEqual(self.planner.dayfile.read(), self.default_weekdaytemplate)
		self.assertEqual(self.planner.weekfile.read(), self.dayadvance_weektemplate)

	def testPlannerAdvanceWeekAgenda(self):
		""" Check that, on day advance, current day's agenda is appended to the current week """
		now = datetime.datetime(2012,12,5,19,0,0)
		self.planner.date = now.date()
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		dayagenda = advanceplanner.extractAgendaFromLogfile(self.planner.dayfile)
		advanceplanner.updateLogfileAgenda(self.planner.weekfile, dayagenda)
		self.assertEqual(self.planner.weekfile.read(), self.weektemplate_agendaupdated)

	def testPlannerAdvanceMonthAgenda(self):
		""" Check that, on week advance, current week's agenda is appended to the current month """
		now = datetime.datetime(2012,12,5,19,0,0)
		self.planner.date = now.date()
		self.planner.weekfile = StringIO(self.weektemplate_agendaupdated)
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		weekagenda = advanceplanner.extractAgendaFromLogfile(self.planner.weekfile)
		advanceplanner.updateLogfileAgenda(self.planner.monthfile, weekagenda)
		self.assertEqual(self.planner.monthfile.read(), self.monthtemplate_agendaupdated)

	def testPlannerAdvanceQuarterAgenda(self):
		""" Check that, on month advance, current month's agenda is appended to the current quarter """
		now = datetime.datetime(2012,12,5,19,0,0)
		self.planner.date = now.date()
		self.planner.monthfile = StringIO(self.monthtemplate_agendaupdated)
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		monthagenda = advanceplanner.extractAgendaFromLogfile(self.planner.monthfile)
		advanceplanner.updateLogfileAgenda(self.planner.quarterfile, monthagenda)
		self.assertEqual(self.planner.quarterfile.read(), self.quartertemplate_agendaupdated)

	def testPlannerAdvanceYearAgenda(self):
		""" Check that, on quarter advance, current quarter's agenda is appended to the current year """
		now = datetime.datetime(2012,12,5,19,0,0)
		self.planner.date = now.date()
		self.planner.quarterfile = StringIO(self.quartertemplate_agendaupdated)
		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.PlannerConfig.LogfileCompletionChecking = advanceplanner.PlannerConfig.Lax
		quarteragenda = advanceplanner.extractAgendaFromLogfile(self.planner.quarterfile)
		advanceplanner.updateLogfileAgenda(self.planner.yearfile, quarteragenda)
		self.assertEqual(self.planner.yearfile.read(), self.yeartemplate_agendaupdated)

class PlannerNewTemplateIntegrityTester(unittest.TestCase):
	""" Check that new templates generated by the planner are as expected """

	tasklist = ("TOMORROW:\n"
					"[ ] contact dude\n"
					"[\] make X\n"
					"[ ] call somebody\n"
					"[ ] finish project\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n")

	tasklist_nextday = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n")

	monthtemplate = ("= December 2012 =\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	weektemplate = ("= WEEK OF DECEMBER 1, 2012 =\n"
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
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

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
					"[x] did do\n"
						"\t[x] this\n"
						"\t[x] and this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you!\n"
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
					"TIME SPENT ON PLANNER: 15 mins")

	checkpoints_month = "[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
	checkpoints_week = "[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
	checkpoints_weekday = ("[ ] 7:00am - wake up []\n[ ] 7:05am - brush + change []\n[ ] 7:10am - protein []\n"
			"[ ] 7:15am - gym []\n[ ] 8:00am - shower []\n[ ] 8:15am - dump []\n"
			"[ ] 11:00pm - (start winding down) brush []\n[ ] 11:05pm - $nasal irrigation$ []\n"
			"[ ] 11:10pm - update schedule []\n[ ] 11:15pm - get stuff ready for morning"
			"((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones"
			") []\n[ ] 11:30pm - sleep []\n")
	checkpoints_weekend = ("[ ] 8:00am - wake up []\n[ ] 8:05am - brush + change []\n[ ] 8:10am - protein []\n"
			"[ ] 8:15am - gym []\n[ ] 9:00am - shower []\n[ ] 9:15am - weigh yourself (saturday) []\n")

	periodic_month = "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
	periodic_week = "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
	periodic_day = "[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule\n"

	def testMonthTemplate(self):
		""" Test that month template is generated correctly by integrating checkpoints, periodic, etc."""
		now = datetime.datetime(2012,12,4,18,50,30)
		today = now.date()
		nextDay = today + datetime.timedelta(days=1)
		tasklistfile = StringIO(self.tasklist)
		checkpointsfile = StringIO(self.checkpoints_month)
		periodicfile = StringIO(self.periodic_month)
		monthfile = StringIO(self.monthtemplate)

		(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
		monthtemplate = "= %s %d =\n" % (month, year)
		monthtemplate += "\n"
		monthtemplate += "\t* [[Week of %s %d, %d]]\n" % (month, date, year)
		monthtemplate += "\n"
		monthtemplate += "CHECKPOINTS:\n"
		monthtemplate += self.checkpoints_month
		monthtemplate += "\n"
		monthtemplate += "AGENDA:\n\n"
		monthtemplate += "MONTHLYs:\n"
		monthtemplate += self.periodic_month
		monthtemplate += "\n"
		monthtemplate += "NOTES:\n\n\n"
		monthtemplate += "TIME SPENT ON PLANNER: "

		advanceplanner.writeNewTemplate(PlannerPeriod.Month, nextDay, tasklistfile, monthfile, checkpointsfile, periodicfile)

		self.assertEqual(monthfile.read(), monthtemplate)

	def testWeekTemplate(self):
		""" Test that week template is generated correctly by integrating checkpoints, periodic, etc."""
		now = datetime.datetime(2012,12,4,18,50,30)
		today = now.date()
		nextDay = today + datetime.timedelta(days=1)
		tasklistfile = StringIO(self.tasklist)
		checkpointsfile = StringIO(self.checkpoints_week)
		periodicfile = StringIO(self.periodic_week)
		weekfile = StringIO(self.weektemplate)

		(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
		weektemplate = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
		weektemplate += "\n"
		weektemplate += "\t* [[%s %d, %d]]\n" % (month, date, year)
		weektemplate += "\n"
		weektemplate += "CHECKPOINTS:\n"
		weektemplate += self.checkpoints_week
		weektemplate += "\n"
		weektemplate += "AGENDA:\n\n"
		weektemplate += "WEEKLYs:\n"
		weektemplate += self.periodic_week
		weektemplate += "\n"
		weektemplate += "NOTES:\n\n\n"
		weektemplate += "TIME SPENT ON PLANNER: "

		advanceplanner.writeNewTemplate(PlannerPeriod.Week, nextDay, tasklistfile, weekfile, checkpointsfile, periodicfile)

		self.assertEqual(weekfile.read(), weektemplate)

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
			tasklistfile = StringIO(self.tasklist)
			if day.lower() in ('saturday', 'sunday'):
				checkpointsfile = StringIO(self.checkpoints_weekend)
			else:
				checkpointsfile = StringIO(self.checkpoints_weekday)
			periodicfile = StringIO(self.periodic_day)
			dayfile = StringIO(self.daytemplate)

			daytemplate = ""
			daytemplate += "CHECKPOINTS:\n"
			if day.lower() in ('saturday', 'sunday'):
				daytemplate += self.checkpoints_weekend
			else:
				daytemplate += self.checkpoints_weekday
			daytemplate += "\n"
			daytemplate += "AGENDA:\n"
			daytemplate += "[ ] s'posed to do\n"
			daytemplate += "[\] kinda did\n"
			daytemplate += "[ ] contact dude\n"
			daytemplate += "[\] make X\n"
			daytemplate += "[ ] call somebody\n"
			daytemplate += "[ ] finish project\n"
			daytemplate += "\n"
			daytemplate += "DAILYs:\n"
			daytemplate += self.periodic_day
			daytemplate += "\n"
			daytemplate += "NOTES:\n\n\n"
			daytemplate += "TIME SPENT ON PLANNER: "

			advanceplanner.writeNewTemplate(PlannerPeriod.Day, nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile)

			self.assertEqual(dayfile.read(), daytemplate)
			self.assertEqual(tasklistfile.read(), self.tasklist_nextday)

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
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	monthtemplate_updated = ("= December 2012 =\n"
					"\t* [[Week of December 5, 2012]]\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

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
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

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
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	def testUpdateExistingMonthTemplate(self):
		""" Check that writing over an existing month template adds the new week, and that there are no other changes """
		now = datetime.datetime(2012,12,4,18,50,30)
		today = now.date()
		nextDay = today + datetime.timedelta(days=1)
		(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
		monthfile = StringIO(self.monthtemplate)
		advanceplanner.writeExistingMonthTemplate(nextDay, monthfile)
		self.assertEqual(monthfile.read(), self.monthtemplate_updated)

	def testUpdateExistingWeekTemplate(self):
		""" Check that writing over an existing week template adds the new day, and that there are no other changes """
		now = datetime.datetime(2012,12,4,18,50,30)
		today = now.date()
		nextDay = today + datetime.timedelta(days=1)
		(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
		weekfile = StringIO(self.weektemplate)
		advanceplanner.writeExistingWeekTemplate(nextDay, weekfile)
		self.assertEqual(weekfile.read(), self.weektemplate_updated)

class PlannerTaskSchedulingTester(unittest.TestCase):
	# TODO: test when week of is set at an actual sunday, and at 1st of month
	# TODO: "first/second/third/fourth week of month"
	# TODO: "next week/month/year"

	tasklist = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n")

	tasklist_tomorrow = ("TOMORROW:\n"
					"[ ] contact dude\n"
					"[\] make X\n"
					"[o] call somebody [$DECEMBER 12, 2012$]\n"
					"[o] apply for something [DECEMBER 26, 2012]\n"
					"[ ] finish project\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n")

	tasklist_scheduledbadformat = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[ ] remember to do this\n")

	tasklist_somescheduled = ("TOMORROW:\n"
					"[ ] contact dude\n"
					"[\] make X\n"
					"[o] call somebody [$DECEMBER 12, 2012$]\n"
					"[o] apply for something [DECEMBER 26, 2012]\n"
					"[ ] finish project\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[o] some misplaced scheduled task [$DECEMBER 14, 2012$]\n"
					"[o] another scheduled task that's lost its way [$DECEMBER 19, 2012$]\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n")

	tasklist_agenda = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[o] i'm waitin on you! [$DECEMBER 20, 2012$]\n"
					"[o] still waitin on you [$JANUARY 14, 2013$]\n")

	tasklist_tasklist = ("TOMORROW:\n"
					"[ ] contact dude\n"
					"[\] make X\n"
					"[o] call somebody [$DECEMBER 12, 2012$]\n"
					"[o] apply for something [DECEMBER 26, 2012]\n"
					"[ ] finish project\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[o] some misplaced scheduled task [$DECEMBER 14, 2012$]\n"
					"[o] another scheduled task that's lost its way [$DECEMBER 19, 2012$]\n")

	tasklist_tasklist_agenda = ("TOMORROW:\n"
					"[ ] contact dude\n"
					"[\] make X\n"
					"[o] call somebody [$DECEMBER 12, 2012$]\n"
					"[o] apply for something [DECEMBER 26, 2012]\n"
					"[ ] finish project\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[o] some misplaced scheduled task [$DECEMBER 14, 2012$]\n"
					"[o] another scheduled task that's lost its way [$DECEMBER 19, 2012$]\n"
					"[o] i'm waitin on you! [$DECEMBER 20, 2012$]\n"
					"[o] still waitin on you [$JANUARY 14, 2013$]\n")

	tasklist_scheduled_formats1to4and11to13 = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[o] i'm waitin on you! [$DECEMBER 20, 2012$]\n"
					"[o] still waitin on you [$JANUARY 14, 2013$]\n")

	tasklist_scheduled_formats5to8and14 = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[o] i'm waitin on you! [$WEEK OF DECEMBER 16, 2012$]\n"
					"[o] still waitin on you [$WEEK OF JANUARY 13, 2013$]\n")

	tasklist_scheduled_formats9to10and15 = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[o] i'm waitin on you! [$DECEMBER 2012$]\n"
					"[o] still waitin on you [$JANUARY 2013$]\n")

	tasklist_scheduled_formats16and17 = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[o] i'm waitin till monday! [$DECEMBER 10, 2012$]\n"
					"[o] i'm waitin till tuesday! [$DECEMBER 4, 2012$]\n"
					"[o] i'm waitin till wednesday! [$DECEMBER 5, 2012$]\n"
					"[o] i'm waitin till thursday! [$DECEMBER 6, 2012$]\n"
					"[o] i'm waitin till friday! [$DECEMBER 7, 2012$]\n"
					"[o] i'm waitin till saturday! [$DECEMBER 8, 2012$]\n"
					"[o] i'm waitin till sunday! [$DECEMBER 9, 2012$]\n")

	yeartemplate = ("= 2012 =\n"
					"\t* [[Q4 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] Q1 - []\n[ ] Q2 - []\n[ ] Q3 - []\n[ ] Q4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"YEARLYs:\n"
					"[ ] 1 significant life achievement\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	quartertemplate = ("= Q4 2012 =\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] MONTH 1 - []\n[ ] MONTH 2 - []\n[ ] MONTH 3 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"QUARTERLYs:\n"
					"[ ] 1 major research achievement\n[ ] 1 major coding achievement\n[ ] 1 unique achievement\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	monthtemplate = ("= December 2012 =\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

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
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	daytemplate = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$DECEMBER 20, 2012$]\n"
					"[o] still waitin on you [$JANUARY 14, 2013$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format1 = daytemplate_scheduled

	daytemplate_scheduled_format2 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$20 DECEMBER, 2012$]\n"
					"[o] still waitin on you [$14 JANUARY, 2013$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format3 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$DECEMBER 20$]\n"
					"[o] still waitin on you [$JANUARY 14$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format4 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$20 DECEMBER$]\n"
					"[o] still waitin on you [$14 JANUARY$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format5 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$WEEK OF DECEMBER 20, 2012$]\n"
					"[o] still waitin on you [$WEEK OF JANUARY 14, 2013$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format6 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$WEEK OF 20 DECEMBER, 2012$]\n"
					"[o] still waitin on you [$WEEK OF 14 JANUARY, 2013$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format7 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$WEEK OF DECEMBER 20$]\n"
					"[o] still waitin on you [$WEEK OF JANUARY 14$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format8 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$WEEK OF 20 DECEMBER$]\n"
					"[o] still waitin on you [$WEEK OF 14 JANUARY$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format9 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$DECEMBER 2012$]\n"
					"[o] still waitin on you [$JANUARY 2013$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format10 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$DECEMBER$]\n"
					"[o] still waitin on you [$JANUARY$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format11 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$12/20/2012$]\n"
					"[o] still waitin on you [$01/14/2013$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format12 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$12-20-2012$]\n"
					"[o] still waitin on you [$01-14-2013$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format13 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$TOMORROW$]\n"
					"[o] still waitin on you [$01-14-2013$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format14 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$NEXT WEEK$]\n"
					"[o] still waitin on you [$WEEK OF JANUARY 14$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format15 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$DECEMBER 2012$]\n"
					"[o] still waitin on you [$NEXT MONTH$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format16 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin till monday! [$MONDAY$]\n"
					"[o] i'm waitin till tuesday! [$TUESDAY$]\n"
					"[o] i'm waitin till wednesday! [$WEDNESDAY$]\n"
					"[o] i'm waitin till thursday! [$THURSDAY$]\n"
					"[o] i'm waitin till friday! [$FRIDAY$]\n"
					"[o] i'm waitin till saturday! [$SATURDAY$]\n"
					"[o] i'm waitin till sunday! [$SUNDAY$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_scheduled_format17 = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin till monday! [$MON$]\n"
					"[o] i'm waitin till tuesday! [$TUE$]\n"
					"[o] i'm waitin till wednesday! [$WED$]\n"
					"[o] i'm waitin till thursday! [$THU$]\n"
					"[o] i'm waitin till friday! [$FRI$]\n"
					"[o] i'm waitin till saturday! [$SAT$]\n"
					"[o] i'm waitin till sunday! [$SUN$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_noscheduledate = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you!\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	checkpoints_year = "[ ] Q1 - []\n[ ] Q2 - []\n[ ] Q3 - []\n[ ] Q4 - []\n"
	checkpoints_quarter = "[ ] MONTH 1 - []\n[ ] MONTH 2 - []\n[ ] MONTH 3 - []\n"
	checkpoints_month = "[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
	checkpoints_week = "[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
	checkpoints_weekday = ("[ ] 7:00am - wake up []\n[ ] 7:05am - brush + change []\n[ ] 7:10am - protein []\n"
			"[ ] 7:15am - gym []\n[ ] 8:00am - shower []\n[ ] 8:15am - dump []\n"
			"[ ] 11:00pm - (start winding down) brush []\n[ ] 11:05pm - $nasal irrigation$ []\n"
			"[ ] 11:10pm - update schedule []\n[ ] 11:15pm - get stuff ready for morning"
			"((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones"
			") []\n[ ] 11:30pm - sleep []\n")
	checkpoints_weekend = ("[ ] 8:00am - wake up []\n[ ] 8:05am - brush + change []\n[ ] 8:10am - protein []\n"
			"[ ] 8:15am - gym []\n[ ] 9:00am - shower []\n[ ] 9:15am - weigh yourself (saturday) []\n")

	periodic_year = "[ ] 1 significant life achievement\n"
	periodic_quarter = "[ ] 1 major research achievement\n[ ] 1 major coding achievement\n[ ] 1 unique achievement\n[ ] update financials\n"
	periodic_month = "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
	periodic_week = "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
	periodic_day = "[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule\n"

	def setUp(self):
		self.planner = Planner()
		self.planner.date = datetime.date(2012,12,19)
		self.planner.tasklistfile = StringIO(self.tasklist)
		self.planner.dayfile = StringIO(self.daytemplate)
		self.planner.weekfile = StringIO(self.weektemplate)
		self.planner.monthfile = StringIO(self.monthtemplate)
		self.planner.quarterfile = StringIO(self.quartertemplate)
		self.planner.yearfile = StringIO(self.yeartemplate)
		self.planner.checkpoints_year_file = StringIO(self.checkpoints_year)
		self.planner.checkpoints_quarter_file = StringIO(self.checkpoints_quarter)
		self.planner.checkpoints_month_file = StringIO(self.checkpoints_month)
		self.planner.checkpoints_week_file = StringIO(self.checkpoints_week)
		self.planner.checkpoints_weekday_file = StringIO(self.checkpoints_weekday)
		self.planner.checkpoints_weekend_file = StringIO(self.checkpoints_weekend)
		self.planner.periodic_year_file = StringIO(self.periodic_year)
		self.planner.periodic_quarter_file = StringIO(self.periodic_quarter)
		self.planner.periodic_month_file = StringIO(self.periodic_month)
		self.planner.periodic_week_file = StringIO(self.periodic_week)
		self.planner.periodic_day_file = StringIO(self.periodic_day)

	def testAgendaScheduledTasksAreScheduled(self):
		""" Check that scheduling tasks pulls all scheduled tasks from today's Agenda
		into the SCHEDULED section of the tasklist """
		now = datetime.datetime(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_agenda)

	def testTaskListScheduledTasksAreScheduled(self):
		""" Check that scheduling tasks pulls all scheduled tasks from the TaskList
		into the SCHEDULED section of the tasklist """
		now = datetime.datetime(2012,12,3)
		self.planner.tasklistfile = StringIO(self.tasklist_somescheduled)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_tasklist)

	def testBothAgendaAndTaskListScheduledTasksAreScheduled(self):
		""" Check that scheduling tasks pulls all scheduled tasks from the TaskList and
		today's agenda into the SCHEDULED section of the tasklist """
		now = datetime.datetime(2012,12,3)
		self.planner.tasklistfile = StringIO(self.tasklist_somescheduled)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_tasklist_agenda)

	def testScheduledTaskWithoutDateRaisesException(self):
		""" Check that is a task is marked as scheduled but no date is provided, that
		an exception is thrown """
		self.planner.dayfile = StringIO(self.daytemplate_noscheduledate)
		self.assertRaises(Exception, advanceplanner.scheduleTasks, self.planner)
	
	def testBadlyFormattedScheduledTaskRaisesException(self):
		""" Check that a task already present in the SCHEDULED section and formatted incorrectly raises an Exception """
		self.planner.tasklistfile = StringIO(self.tasklist_scheduledbadformat)
		self.assertRaises(Exception, advanceplanner.scheduleTasks, self.planner)

	def testScheduleDateFormat1(self):
		""" Check that the format MONTH DD, YYYY works (w optional space or comma or both) """
		now = datetime.datetime(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format1)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats1to4and11to13)

	def testScheduleDateFormat2(self):
		""" Check that the format DD MONTH, YYYY works (w optional space or comma or both) """
		now = datetime.datetime(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format2)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats1to4and11to13)

	def testScheduleDateFormat3(self):
		""" Check that the format MONTH DD works """
		now = datetime.datetime(2012,12,21)
		self.planner.date = datetime.date(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format3)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats1to4and11to13)

	def testScheduleDateFormat4(self):
		""" Check that the format DD MONTH works """
		now = datetime.datetime(2012,12,21)
		self.planner.date = datetime.date(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format4)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats1to4and11to13)

	def testScheduleDateFormat5(self):
		""" Check that the format WEEK OF MONTH DD, YYYY works (w optional space or comma or both) """
		now = datetime.datetime(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format5)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats5to8and14)

	def testScheduleDateFormat6(self):
		""" Check that the format WEEK OF DD MONTH, YYYY works (w optional space or comma or both) """
		now = datetime.datetime(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format6)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats5to8and14)

	def testScheduleDateFormat7(self):
		""" Check that the format WEEK OF MONTH DD works """
		now = datetime.datetime(2012,12,21)
		self.planner.date = datetime.date(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format7)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats5to8and14)

	def testScheduleDateFormat8(self):
		""" Check that the format WEEK OF DD MONTH works """
		now = datetime.datetime(2012,12,21)
		self.planner.date = datetime.date(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format8)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats5to8and14)

	def testScheduleDateFormat9(self):
		""" Check that the format MONTH YYYY works (w optional space or comma or both) """
		now = datetime.datetime(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format9)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats9to10and15)

	def testScheduleDateFormat10(self):
		""" Check that the format MONTH works """
		now = datetime.datetime(2012,12,3)
		self.planner.date = datetime.date(2012,11,4)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format10)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats9to10and15)

	def testScheduleDateFormat11(self):
		""" Check that the format MM/DD/YYYY works """
		now = datetime.datetime(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format11)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats1to4and11to13)

	def testScheduleDateFormat12(self):
		""" Check that the format MM-DD-YYYY works """
		now = datetime.datetime(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format12)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats1to4and11to13)

	def testScheduleDateFormat13(self):
		""" Check that the format TOMORROW works """
		now = datetime.datetime(2012,12,20) # schedule date should be wrt planner date, not current time
		self.planner.date = datetime.date(2012,12,19)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format13)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats1to4and11to13)

	def testScheduleDateFormat14(self):
		""" Check that the format NEXT WEEK works """
		now = datetime.datetime(2012,12,17)
		self.planner.date = datetime.date(2012,12,10)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format14)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats5to8and14)

	def testScheduleDateFormat15(self):
		""" Check that the format NEXT MONTH works """
		now = datetime.datetime(2013,1,1)
		self.planner.date = datetime.date(2012,12,3)
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format15)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats9to10and15)

	def testScheduleDateFormat16(self):
		""" Check that the format <DOW> works """
		now = datetime.datetime(2012,12,4) # tuesday
		self.planner.date = datetime.date(2012,12,3) # monday
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format16)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats16and17)

	def testScheduleDateFormat17(self):
		""" Check that the format <DOW> (abbrv.) works """
		now = datetime.datetime(2012,12,4) # tuesday
		self.planner.date = datetime.date(2012,12,3) # monday
		self.planner.dayfile = StringIO(self.daytemplate_scheduled_format17)
		advanceplanner.scheduleTasks(self.planner, now)
		self.assertEqual(self.planner.tasklistfile.read(), self.tasklist_scheduled_formats16and17)

class PlannerAgendaConstructionTester(unittest.TestCase):

	tasklist = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n")

	tasklist_tomorrow = ("TOMORROW:\n"
					"[ ] contact dude\n"
					"[\] make X\n"
					"[o] call somebody [$DECEMBER 12, 2012$]\n"
					"[o] apply for something [DECEMBER 26, 2012]\n"
					"[ ] finish project\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n")

	tasklist_somescheduled = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[o] this task is for some day but probably not the day you're looking for [$DECEMBER 15, 2012$]\n"
					"[o] this task is def not the one you need to do [$DECEMBER 19, 2012$]\n")

	tasklist_scheduledfortomorrow = ("TOMORROW:\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[o] this is an old task that should have been done long ago! [$DECEMBER 3, 2012$]\n"
					"[o] this task could be the one you need to do! [$DECEMBER 10, 2012$]\n"
					"[o] here's one that should be pulled up [$WEEK OF DECEMBER 9, 2012$]\n"
					"[o] here's one that shouldn't be pulled up [$WEEK OF DECEMBER 16, 2012$]\n")

	tasklist_tomorrowscheduled = ("TOMORROW:\n"
					"[ ] contact dude\n"
					"[\] make X\n"
					"[o] call somebody [$DECEMBER 12, 2012$]\n"
					"[o] apply for something [DECEMBER 26, 2012]\n"
					"[ ] finish project\n"
					"\n"
					"THIS WEEK:\n"
					"[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
					"[ ] help meags set up planner\n"
						"\t[x] create life mindmap with meags\n"
						"\t[x] incorporate life mindmap into planner with meags\n"
						"\t[x] swap meags' Esc and CapsLock on personal laptop\n"
						"\t[x] vim education and workflow\n"
						"\t[x] help meags build a routine of entering data for the day\n"
						"\t[ ] meags to schedule all activities (currently unscheduled)\n"
						"\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
						"\t[-] set up git access on your domain\n"
						"\t[ ] set up dropbox+truecrypt planner access for meags\n"
					"\n"
					"THIS MONTH:\n"
					"[ ] get India Tour reimbursement\n"
						"\t[x] resend all receipts and info to Amrit\n"
						"\t[x] send reminder email to Amrit\n"
						"\t[x] coordinate with amrit to go to stanford campus\n"
						"\t[x] remind amrit if no response\n"
						"\t[x] check Stanford calendar for appropriate time\n"
						"\t[x] email amrit re: thursday?\n"
						"\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
						"\t[x] wait for response\n"
						"\t[-] send reminder on Wed night\n"
						"\t[x] respond to amrit's email re: amount correction\n"
						"\t[x] wait to hear back [remind $MONDAY$]\n"
						"\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
						"\t[x] pick up reimbursement, give difference check to raag\n"
						"\t[x] cash check\n"
						"\t[x] confirm deposit\n"
						"\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
					"[ ] do residual monthlys\n"
					"[ ] get a good scratchy post for ferdy (fab?)\n"
					"\n"
					"UNSCHEDULED:\n"
					"\n"
					"SCHEDULED:\n"
					"[o] this task is for some day but probably not the day you're looking for [$DECEMBER 15, 2012$]\n"
					"[o] this is an old task that should have been done long ago! [$DECEMBER 3, 2012$]\n"
					"[o] this task could be the one you need to do! [$DECEMBER 10, 2012$]\n"
					"[o] this task is def not the one you need to do [$DECEMBER 19, 2012$]\n")

	monthtemplate = ("= December 2012 =\n"
					"\t* [[Week of December 1, 2012]]\n"
					"\n"
					"CHECKPOINTS:\n"
					"[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
					"\n"
					"AGENDA:\n"
					"\n"
					"MONTHLYs:\n"
					"[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

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
					"WEEKLYs:\n"
					"[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
					"\n"
					"NOTES:\n"
					"\n\n"
					"TIME SPENT ON PLANNER: ")

	daytemplate = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	daytemplate_undone = ("CHECKPOINTS:\n"
					"[x] 7:00am - wake up [9:00]\n"
					"\n"
					"AGENDA:\n"
					"[x] did do\n"
						"\t[x] this\n"
					"[ ] s'posed to do\n"
					"[\] kinda did\n"
					"[o] i'm waitin on you! [$DECEMBER 20, 2012$]\n"
					"[x] take out trash\n"
					"\n"
					"DAILYs:\n"
					"[ ] 40 mins gym\n"
					"\n"
					"NOTES:\n"
					"\n"
					"\n"
					"TIME SPENT ON PLANNER: 15 mins")

	checkpoints_month = "[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
	checkpoints_week = "[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
	checkpoints_weekday = ("[ ] 7:00am - wake up []\n[ ] 7:05am - brush + change []\n[ ] 7:10am - protein []\n"
			"[ ] 7:15am - gym []\n[ ] 8:00am - shower []\n[ ] 8:15am - dump []\n"
			"[ ] 11:00pm - (start winding down) brush []\n[ ] 11:05pm - $nasal irrigation$ []\n"
			"[ ] 11:10pm - update schedule []\n[ ] 11:15pm - get stuff ready for morning"
			"((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones"
			") []\n[ ] 11:30pm - sleep []\n")
	checkpoints_weekend = ("[ ] 8:00am - wake up []\n[ ] 8:05am - brush + change []\n[ ] 8:10am - protein []\n"
			"[ ] 8:15am - gym []\n[ ] 9:00am - shower []\n[ ] 9:15am - weigh yourself (saturday) []\n")

	periodic_month = "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
	periodic_week = "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
	periodic_day = "[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule\n"

	def testAgendaIsEmptyWhenTomorrowAndUndoneAreEmpty(self):
		""" Check that tomorrow's agenda is empty when no tasks are undone from today, and no tasks have been added for tomorrow """
		nextDay = datetime.date(2012,12,10)
		tasklistfile = StringIO(self.tasklist)
		dayfile = StringIO(self.daytemplate)
		checkpointsfile = StringIO(self.checkpoints_weekday)
		periodicfile = StringIO(self.periodic_day)
		checkpointsfile = StringIO(self.checkpoints_weekday)

		daytemplate = ""
		daytemplate += "CHECKPOINTS:\n"
		daytemplate += self.checkpoints_weekday
		daytemplate += "\n"
		daytemplate += "AGENDA:\n"
		daytemplate += "\n"
		daytemplate += "DAILYs:\n"
		daytemplate += self.periodic_day
		daytemplate += "\n"
		daytemplate += "NOTES:\n\n\n"
		daytemplate += "TIME SPENT ON PLANNER: "

		advanceplanner.writeNewTemplate(PlannerPeriod.Day, nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile)

		self.assertEqual(dayfile.read(), daytemplate)

	def testAgendaHasUndoneTasks(self):
		""" Check that any undone tasks from today are carried over to tomorrow's agenda """
		nextDay = datetime.date(2012,12,10)
		tasklistfile = StringIO(self.tasklist)
		dayfile = StringIO(self.daytemplate_undone)
		checkpointsfile = StringIO(self.checkpoints_weekday)
		periodicfile = StringIO(self.periodic_day)
		checkpointsfile = StringIO(self.checkpoints_weekday)

		daytemplate = ""
		daytemplate += "CHECKPOINTS:\n"
		daytemplate += self.checkpoints_weekday
		daytemplate += "\n"
		daytemplate += "AGENDA:\n"
		daytemplate += "[ ] s'posed to do\n"
		daytemplate += "[\] kinda did\n"
		daytemplate += "\n"
		daytemplate += "DAILYs:\n"
		daytemplate += self.periodic_day
		daytemplate += "\n"
		daytemplate += "NOTES:\n\n\n"
		daytemplate += "TIME SPENT ON PLANNER: "

		advanceplanner.writeNewTemplate(PlannerPeriod.Day, nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile)

		self.assertEqual(dayfile.read(), daytemplate)

	def testAgendaHasTomorrowsTasks(self):
		""" Check that tomorrow's agenda has tasks added for tomorrow """
		nextDay = datetime.date(2012,12,10)
		tasklistfile = StringIO(self.tasklist_tomorrow)
		dayfile = StringIO(self.daytemplate)
		checkpointsfile = StringIO(self.checkpoints_weekday)
		periodicfile = StringIO(self.periodic_day)
		checkpointsfile = StringIO(self.checkpoints_weekday)

		daytemplate = ""
		daytemplate += "CHECKPOINTS:\n"
		daytemplate += self.checkpoints_weekday
		daytemplate += "\n"
		daytemplate += "AGENDA:\n"
		daytemplate += "[ ] contact dude\n"
		daytemplate += "[\] make X\n"
		daytemplate += "[o] call somebody [$DECEMBER 12, 2012$]\n"
		daytemplate += "[o] apply for something [DECEMBER 26, 2012]\n"
		daytemplate += "[ ] finish project\n"
		daytemplate += "\n"
		daytemplate += "DAILYs:\n"
		daytemplate += self.periodic_day
		daytemplate += "\n"
		daytemplate += "NOTES:\n\n\n"
		daytemplate += "TIME SPENT ON PLANNER: "

		advanceplanner.writeNewTemplate(PlannerPeriod.Day, nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile)

		self.assertEqual(dayfile.read(), daytemplate)

	def testAgendaHasBothTomorrowsTasksAndUndoneTasks(self):
		""" Check that tomorrow's agenda has both undone tasks from today's agenda as well as tasks added for tomorrow """
		nextDay = datetime.date(2012,12,10)
		tasklistfile = StringIO(self.tasklist_tomorrow)
		dayfile = StringIO(self.daytemplate_undone)
		checkpointsfile = StringIO(self.checkpoints_weekday)
		periodicfile = StringIO(self.periodic_day)
		checkpointsfile = StringIO(self.checkpoints_weekday)

		daytemplate = ""
		daytemplate += "CHECKPOINTS:\n"
		daytemplate += self.checkpoints_weekday
		daytemplate += "\n"
		daytemplate += "AGENDA:\n"
		daytemplate += "[ ] s'posed to do\n"
		daytemplate += "[\] kinda did\n"
		daytemplate += "[ ] contact dude\n"
		daytemplate += "[\] make X\n"
		daytemplate += "[o] call somebody [$DECEMBER 12, 2012$]\n"
		daytemplate += "[o] apply for something [DECEMBER 26, 2012]\n"
		daytemplate += "[ ] finish project\n"
		daytemplate += "\n"
		daytemplate += "DAILYs:\n"
		daytemplate += self.periodic_day
		daytemplate += "\n"
		daytemplate += "NOTES:\n\n\n"
		daytemplate += "TIME SPENT ON PLANNER: "

		advanceplanner.writeNewTemplate(PlannerPeriod.Day, nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile)

		self.assertEqual(dayfile.read(), daytemplate)

	def testAgendaIsEmptyWhenScheduledTasksAreNotForTomorrow(self):
		""" Check that tomorrow's agenda is empty when no scheduled tasks are scheduled for tomorrow 
		(and no new tasks added for tomorrow, no tasks remaining undone from today) """
		nextDay = datetime.date(2012,12,10)
		tasklistfile = StringIO(self.tasklist_somescheduled)
		dayfile = StringIO(self.daytemplate)
		checkpointsfile = StringIO(self.checkpoints_weekday)
		periodicfile = StringIO(self.periodic_day)
		checkpointsfile = StringIO(self.checkpoints_weekday)

		daytemplate = ""
		daytemplate += "CHECKPOINTS:\n"
		daytemplate += self.checkpoints_weekday
		daytemplate += "\n"
		daytemplate += "AGENDA:\n"
		daytemplate += "\n"
		daytemplate += "DAILYs:\n"
		daytemplate += self.periodic_day
		daytemplate += "\n"
		daytemplate += "NOTES:\n\n\n"
		daytemplate += "TIME SPENT ON PLANNER: "

		advanceplanner.writeNewTemplate(PlannerPeriod.Day, nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile)

		self.assertEqual(dayfile.read(), daytemplate)

	def testAgendaContainsTasksScheduledForTomorrow(self):
		""" Check that tomorrow's agenda contains scheduled tasks that are scheduled for tomorrow """
		nextDay = datetime.date(2012,12,10)
		tasklistfile = StringIO(self.tasklist_scheduledfortomorrow)
		dayfile = StringIO(self.daytemplate)
		checkpointsfile = StringIO(self.checkpoints_weekday)
		periodicfile = StringIO(self.periodic_day)
		checkpointsfile = StringIO(self.checkpoints_weekday)

		daytemplate = ""
		daytemplate += "CHECKPOINTS:\n"
		daytemplate += self.checkpoints_weekday
		daytemplate += "\n"
		daytemplate += "AGENDA:\n"
		daytemplate += "[o] this is an old task that should have been done long ago! [$DECEMBER 3, 2012$]\n"
		daytemplate += "[o] this task could be the one you need to do! [$DECEMBER 10, 2012$]\n"
		daytemplate += "[o] here's one that should be pulled up [$WEEK OF DECEMBER 9, 2012$]\n"
		daytemplate += "\n"
		daytemplate += "DAILYs:\n"
		daytemplate += self.periodic_day
		daytemplate += "\n"
		daytemplate += "NOTES:\n\n\n"
		daytemplate += "TIME SPENT ON PLANNER: "

		advanceplanner.PlannerConfig.TomorrowChecking = advanceplanner.PlannerConfig.Lax
		advanceplanner.writeNewTemplate(PlannerPeriod.Day, nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile)

		self.assertEqual(dayfile.read(), daytemplate)

	def testAgendaContainsTomorrowsUndoneAndScheduledTasks(self):
		""" Check that tomorrow's agenda contains undone tasks carried over from today, tasks added for tomorrow, as well as tasks previously scheduled for tomorrow """
		nextDay = datetime.date(2012,12,10)
		tasklistfile = StringIO(self.tasklist_tomorrowscheduled)
		dayfile = StringIO(self.daytemplate_undone)
		checkpointsfile = StringIO(self.checkpoints_weekday)
		periodicfile = StringIO(self.periodic_day)
		checkpointsfile = StringIO(self.checkpoints_weekday)

		daytemplate = ""
		daytemplate += "CHECKPOINTS:\n"
		daytemplate += self.checkpoints_weekday
		daytemplate += "\n"
		daytemplate += "AGENDA:\n"
		daytemplate += "[o] this is an old task that should have been done long ago! [$DECEMBER 3, 2012$]\n"
		daytemplate += "[o] this task could be the one you need to do! [$DECEMBER 10, 2012$]\n"
		daytemplate += "[ ] s'posed to do\n"
		daytemplate += "[\] kinda did\n"
		daytemplate += "[ ] contact dude\n"
		daytemplate += "[\] make X\n"
		daytemplate += "[o] call somebody [$DECEMBER 12, 2012$]\n"
		daytemplate += "[o] apply for something [DECEMBER 26, 2012]\n"
		daytemplate += "[ ] finish project\n"
		daytemplate += "\n"
		daytemplate += "DAILYs:\n"
		daytemplate += self.periodic_day
		daytemplate += "\n"
		daytemplate += "NOTES:\n\n\n"
		daytemplate += "TIME SPENT ON PLANNER: "

		advanceplanner.writeNewTemplate(PlannerPeriod.Day, nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile)

		self.assertEqual(dayfile.read(), daytemplate)


if __name__ == '__main__':
	unittest.main()
