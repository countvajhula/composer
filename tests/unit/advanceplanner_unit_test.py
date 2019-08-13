#!/usr/bin/env python

import unittest
import datetime

import composer.backend.filesystem.advanceplanner as advanceplanner
import composer.config as config
from composer.backend import FilesystemPlanner
from composer.utils import PlannerPeriod

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


# 1. add year later
# 2. improve later to have dif templates for each day -- *day*
# 3. if attempt to create already exists throw exception
# 4. add if (themes) condition
# 5. Check current date and day, get "successor" using python date module (unit tests for this)
# 6. Add tests for different partially-done todos
# 7. Add tests for assert raises, esp in scheduling
# 8. Add tests for logfile completion checking: (1) quarter bug, (2) regexp matches for log (^OCI matched giving logfile incomplete):
#     ASDFADF :,ASFASfdfad:,ASDFASDF:,ASDFSADF adfadf asd: asdfAf,ASDFASDFAF,AASFDFD ASDF:,ASDFFD:ASDFSF,NEW SECTION:,ASDFFD:ASDFSF:,NEW SECTION IS HERE: and some data 5:56


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

    tasklist = (
        "TOMORROW:\n"
        "\n"
        "THIS WEEK:\n"
        "[\\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
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
    )

    yeartemplate = (
        "= 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    yeartemplate_agendaupdated = (
        "= 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    yearadvance_yeartemplate = (
        "= 2013 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    yearadvance_quartertemplate = (
        "= Q1 2013 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    yearadvance_monthtemplate = (
        "= JANUARY 2013 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    yearadvance_weektemplate = (
        "= WEEK OF JANUARY 1, 2013 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    quartertemplate = (
        "= Q4 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    quartertemplate_agendaupdated = (
        "= Q4 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    quarteradvance_yeartemplate = (
        "= 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    quarteradvance_quartertemplate = quartertemplate

    quarteradvance_monthtemplate = (
        "= OCTOBER 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    quarteradvance_weektemplate = (
        "= WEEK OF OCTOBER 1, 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    monthtemplate = (
        "= DECEMBER 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    monthtemplate_agendaupdated = (
        "= DECEMBER 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    monthadvance_monthtemplate = monthtemplate

    monthadvance_weektemplate = (
        "= WEEK OF DECEMBER 1, 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    default_weekdaytemplate = (
        "CHECKPOINTS:\n"
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
        "TIME SPENT ON PLANNER: "
    )

    default_weekendtemplate = (
        "CHECKPOINTS:\n"
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
        "TIME SPENT ON PLANNER: "
    )

    weektemplate = (
        "= WEEK OF DECEMBER 1, 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    weekadvance_weektemplate = (
        "= WEEK OF DECEMBER 9, 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    weekadvance_monthtemplate = (
        "= DECEMBER 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    weektemplate_agendaupdated = (
        "= WEEK OF DECEMBER 1, 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    daytemplate = (
        "CHECKPOINTS:\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    dayadvance_weektemplate = (
        "= WEEK OF DECEMBER 1, 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    checkpoints_year = "[ ] Q1 - []\n[ ] Q2 - []\n[ ] Q3 - []\n[ ] Q4 - []\n"
    checkpoints_quarter = (
        "[ ] MONTH 1 - []\n[ ] MONTH 2 - []\n[ ] MONTH 3 - []\n"
    )
    checkpoints_month = (
        "[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
    )
    checkpoints_week = "[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
    checkpoints_weekday = (
        "[ ] 7:00am - wake up []\n[ ] 7:05am - brush + change []\n[ ] 7:10am - protein []\n"
        "[ ] 7:15am - gym []\n[ ] 8:00am - shower []\n[ ] 8:15am - dump []\n"
        "[ ] 11:00pm - (start winding down) brush []\n[ ] 11:05pm - $nasal irrigation$ []\n"
        "[ ] 11:10pm - update schedule []\n[ ] 11:15pm - get stuff ready for morning"
        "((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones"
        ") []\n[ ] 11:30pm - sleep []\n"
    )
    checkpoints_weekend = (
        "[ ] 8:00am - wake up []\n[ ] 8:05am - brush + change []\n[ ] 8:10am - protein []\n"
        "[ ] 8:15am - gym []\n[ ] 9:00am - shower []\n[ ] 9:15am - weigh yourself (saturday) []\n"
    )

    periodic_year = "[ ] 1 significant life achievement\n"
    periodic_quarter = "[ ] 1 major research achievement\n[ ] 1 major coding achievement\n[ ] 1 unique achievement\n[ ] update financials\n"
    periodic_month = "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
    periodic_week = "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
    periodic_day = "[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule\n"
    daythemes = "SUNDAY: Groceries Day\nMONDAY: \nTUESDAY:Cleaning Day\nWEDNESDAY:\nTHURSDAY:\nFRIDAY:\nSATURDAY: LAUNDRY DAY\n"

    def setUp(self):
        self.planner = FilesystemPlanner()
        self.planner.date = datetime.date.today()
        self.planner.tasklistfile = StringIO(self.tasklist)
        self.planner.daythemesfile = StringIO(self.daythemes)
        self.planner.dayfile = StringIO(self.daytemplate)
        self.planner.weekfile = StringIO(self.weektemplate)
        self.planner.monthfile = StringIO(self.monthtemplate)
        self.planner.quarterfile = StringIO(self.quartertemplate)
        self.planner.yearfile = StringIO(self.yeartemplate)
        self.planner.checkpoints_year_file = StringIO(self.checkpoints_year)
        self.planner.checkpoints_quarter_file = StringIO(
            self.checkpoints_quarter
        )
        self.planner.checkpoints_month_file = StringIO(self.checkpoints_month)
        self.planner.checkpoints_week_file = StringIO(self.checkpoints_week)
        self.planner.checkpoints_weekday_file = StringIO(
            self.checkpoints_weekday
        )
        self.planner.checkpoints_weekend_file = StringIO(
            self.checkpoints_weekend
        )
        self.planner.periodic_year_file = StringIO(self.periodic_year)
        self.planner.periodic_quarter_file = StringIO(self.periodic_quarter)
        self.planner.periodic_month_file = StringIO(self.periodic_month)
        self.planner.periodic_week_file = StringIO(self.periodic_week)
        self.planner.periodic_day_file = StringIO(self.periodic_day)

    def test_decision_for_typical_day_advance(self):
        """ Check that planner advance takes the correct decision to advance day on a typical day change boundary """
        now = datetime.datetime(2012, 12, 5, 19, 0, 0)
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]  # seems this happens even without declaring it here - need to reset these in tearDown()
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Day)

    def test_decision_for_first_week_too_short_day_advance(self):
        """ Check that planner advance takes the correct decision to advance only day when first week is too short """
        now = datetime.datetime(
            2012, 3, 3, 19, 0, 0
        )  # 3/3/2012 is a Saturday, but since current week is only 3 days (too short), should advance only day
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Day)

    def test_decision_for_first_week_borderline_too_short_day_advance(self):
        """ Check that planner advance takes the correct decision to advance only day when first week is just below minimum length """
        now = datetime.datetime(
            2012, 2, 4, 19, 0, 0
        )  # 2/4/2012 is a Saturday, but since current week is 4 days (just short of requirement), should advance only day
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Day)

    def test_decision_for_last_week_too_short_day_advance(self):
        """ Check that planner advance takes the correct decision to advance only day when last week would be too short """
        now = datetime.datetime(
            2012, 12, 29, 19, 0, 0
        )  # 12/29/2012 is a Saturday, but since new week would be too short, should advance only day
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Day)

    def test_decision_for_last_week_borderline_too_short_day_advance(self):
        """ Check that planner advance takes the correct decision to advance only day when last week would be just below minimum length """
        now = datetime.datetime(
            2012, 2, 25, 19, 0, 0
        )  # 2/25/2012 is a Saturday, but since new week is 4 days (just short of requirement), should advance only day
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Day)

    def test_decision_for_typical_week_advance(self):
        """ Check that planner advance takes the correct decision to advance week on a typical week change boundary """
        now = datetime.datetime(2012, 12, 8, 19, 0, 0)
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Week)

    def test_decision_for_first_week_borderline_long_enough_week_advance(self):
        """ Check that planner advance takes the correct decision to advance week when last week would be just at minimum length """
        now = datetime.datetime(
            2012, 5, 5, 19, 0, 0
        )  # 5/5/2012 is Sat, and current week is exactly 5 days long (long enough), so should advance week
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Week)

    def test_decision_for_last_week_borderline_long_enough_week_advance(self):
        """ Check that planner advance takes the correct decision to advance week when last week would be just at minimum length """
        now = datetime.datetime(
            2012, 5, 26, 19, 0, 0
        )  # 5/26/2012 is Sat, and new week would be exactly 5 days long (long enough), so should advance week
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Week)

    def test_decision_for_month_advance(self):
        """ Check that planner advance takes the correct decision to advance month on a month change boundary """
        now = datetime.datetime(2012, 11, 30, 19, 0, 0)
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Month)

    def test_decision_for_quarter_advance(self):
        """ Check that planner advance takes the correct decision to advance quarter on a quarter change boundary """
        now = datetime.datetime(2012, 3, 31, 19, 0, 0)
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Quarter)

    def test_decision_for_year_advance(self):
        """ Check that planner advance takes the correct decision to advance year on a year change boundary """
        now = datetime.datetime(2012, 12, 31, 19, 0, 0)
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(status, PlannerPeriod.Year)

    def test_planner_advance_year(self):
        """ Check that planner advance returns the correct new year, quarter, month, week, and day templates when advancing year """
        now = datetime.datetime(2012, 12, 31, 19, 0, 0)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        dailythemes = self.daythemes.lower()
        theme = dailythemes[dailythemes.index(day.lower()) :]
        theme = theme[theme.index(':') :].strip(': ')
        theme = theme[: theme.index('\n')].strip().upper()
        theme = "*" + theme + "*"
        daytemplate = ""
        daytemplate += "= %s %s %d, %d =\n" % (
            day.upper(),
            month[:3].upper(),
            date,
            year,
        )
        daytemplate += "\n"
        if len(theme) > 2:
            daytemplate += "Theme: %s\n" % theme
            daytemplate += "\n"
        daytemplate += self.default_weekdaytemplate
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]

        advanceplanner.advance_planner(self.planner, now)

        self.assertEqual(
            self.planner.yearfile.read(), self.yearadvance_yeartemplate
        )
        self.assertEqual(
            self.planner.quarterfile.read(), self.yearadvance_quartertemplate
        )
        self.assertEqual(
            self.planner.monthfile.read(), self.yearadvance_monthtemplate
        )
        self.assertEqual(
            self.planner.weekfile.read(), self.yearadvance_weektemplate
        )
        self.assertEqual(self.planner.dayfile.read(), daytemplate)

    def test_planner_advance_quarter(self):
        """ Check that planner advance returns the correct new quarter, month, week, and day templates when advancing quarter """
        now = datetime.datetime(2012, 9, 30, 19, 0, 0)
        self.planner.date = now.date()
        today = now.date()
        next_day = today + datetime.timedelta(days=1)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        dailythemes = self.daythemes.lower()
        theme = dailythemes[dailythemes.index(day.lower()) :]
        theme = theme[theme.index(':') :].strip(': ')
        theme = theme[: theme.index('\n')].strip().upper()
        theme = "*" + theme + "*"
        daytemplate = ""
        daytemplate += "= %s %s %d, %d =\n" % (
            day.upper(),
            month[:3].upper(),
            date,
            year,
        )
        daytemplate += "\n"
        if len(theme) > 2:
            daytemplate += "Theme: %s\n" % theme
            daytemplate += "\n"
        daytemplate += self.default_weekdaytemplate
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(
            self.planner.quarterfile.read(),
            self.quarteradvance_quartertemplate,
        )
        self.assertEqual(
            self.planner.monthfile.read(), self.quarteradvance_monthtemplate
        )
        self.assertEqual(
            self.planner.weekfile.read(), self.quarteradvance_weektemplate
        )
        self.assertEqual(self.planner.dayfile.read(), daytemplate)

    def test_planner_advance_month(self):
        """ Check that planner advance returns the correct new month, week, and day templates when advancing month """
        now = datetime.datetime(2012, 11, 30, 19, 0, 0)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        dailythemes = self.daythemes.lower()
        theme = dailythemes[dailythemes.index(day.lower()) :]
        theme = theme[theme.index(':') :].strip(': ')
        theme = theme[: theme.index('\n')].strip().upper()
        theme = "*" + theme + "*"
        daytemplate = ""
        daytemplate += "= %s %s %d, %d =\n" % (
            day.upper(),
            month[:3].upper(),
            date,
            year,
        )
        daytemplate += "\n"
        if len(theme) > 2:
            daytemplate += "Theme: %s\n" % theme
            daytemplate += "\n"
        daytemplate += self.default_weekendtemplate
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(
            self.planner.monthfile.read(), self.monthadvance_monthtemplate
        )
        self.assertEqual(
            self.planner.weekfile.read(), self.monthadvance_weektemplate
        )
        self.assertEqual(self.planner.dayfile.read(), daytemplate)

    def test_planner_advance_week(self):
        """ Check that planner advance returns the correct new week and day templates, and updates the existing month template correctly, when advancing week """
        now = datetime.datetime(2012, 12, 8, 19, 0, 0)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        dailythemes = self.daythemes.lower()
        theme = dailythemes[dailythemes.index(day.lower()) :]
        theme = theme[theme.index(':') :].strip(': ')
        theme = theme[: theme.index('\n')].strip().upper()
        theme = "*" + theme + "*"
        daytemplate = ""
        daytemplate += "= %s %s %d, %d =\n" % (
            day.upper(),
            month[:3].upper(),
            date,
            year,
        )
        daytemplate += "\n"
        if len(theme) > 2:
            daytemplate += "Theme: %s\n" % theme
            daytemplate += "\n"
        daytemplate += self.default_weekendtemplate
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        status = advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(
            self.planner.weekfile.read(), self.weekadvance_weektemplate
        )
        self.assertEqual(
            self.planner.monthfile.read(), self.weekadvance_monthtemplate
        )
        self.assertEqual(self.planner.dayfile.read(), daytemplate)

    def test_planner_advance_day(self):
        """ Check that planner advance returns the correct new day template, and updates the existing week template, when advancing day """
        now = datetime.datetime(2012, 12, 5, 19, 0, 0)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        dailythemes = self.daythemes.lower()
        theme = dailythemes[dailythemes.index(day.lower()) :]
        theme = theme[theme.index(':') :].strip(': ')
        theme = theme[: theme.index('\n')].strip().upper()
        theme = "*" + theme + "*"
        daytemplate = ""
        daytemplate += "= %s %s %d, %d =\n" % (
            day.upper(),
            month[:3].upper(),
            date,
            year,
        )
        daytemplate += "\n"
        if len(theme) > 2:
            daytemplate += "Theme: %s\n" % theme
            daytemplate += "\n"
        daytemplate += self.default_weekdaytemplate
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        advanceplanner.advance_planner(self.planner, now)
        self.assertEqual(self.planner.dayfile.read(), daytemplate)
        self.assertEqual(
            self.planner.weekfile.read(), self.dayadvance_weektemplate
        )

    def test_planner_advance_week_agenda(self):
        """ Check that, on day advance, current day's agenda is appended to the current week """
        now = datetime.datetime(2012, 12, 5, 19, 0, 0)
        self.planner.date = now.date()
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        dayagenda = advanceplanner.extract_agenda_from_logfile(
            self.planner.dayfile
        )
        logfile = advanceplanner.update_logfile_agenda(
            self.planner.weekfile, dayagenda
        )
        self.assertEqual(logfile.read(), self.weektemplate_agendaupdated)

    def test_planner_advance_month_agenda(self):
        """ Check that, on week advance, current week's agenda is appended to the current month """
        now = datetime.datetime(2012, 12, 5, 19, 0, 0)
        self.planner.date = now.date()
        self.planner.weekfile = StringIO(self.weektemplate_agendaupdated)
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        weekagenda = advanceplanner.extract_agenda_from_logfile(
            self.planner.weekfile
        )
        logfile = advanceplanner.update_logfile_agenda(
            self.planner.monthfile, weekagenda
        )
        self.assertEqual(logfile.read(), self.monthtemplate_agendaupdated)

    def test_planner_advance_quarter_agenda(self):
        """ Check that, on month advance, current month's agenda is appended to the current quarter """
        now = datetime.datetime(2012, 12, 5, 19, 0, 0)
        self.planner.date = now.date()
        self.planner.monthfile = StringIO(self.monthtemplate_agendaupdated)
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        monthagenda = advanceplanner.extract_agenda_from_logfile(
            self.planner.monthfile
        )
        logfile = advanceplanner.update_logfile_agenda(
            self.planner.quarterfile, monthagenda
        )
        self.assertEqual(logfile.read(), self.quartertemplate_agendaupdated)

    def test_planner_advance_year_agenda(self):
        """ Check that, on quarter advance, current quarter's agenda is appended to the current year """
        now = datetime.datetime(2012, 12, 5, 19, 0, 0)
        self.planner.date = now.date()
        self.planner.quarterfile = StringIO(self.quartertemplate_agendaupdated)
        self.planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        quarteragenda = advanceplanner.extract_agenda_from_logfile(
            self.planner.quarterfile
        )
        logfile = advanceplanner.update_logfile_agenda(
            self.planner.yearfile, quarteragenda
        )
        self.assertEqual(logfile.read(), self.yeartemplate_agendaupdated)


if __name__ == '__main__':
    unittest.main()
