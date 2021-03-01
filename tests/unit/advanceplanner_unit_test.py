#!/usr/bin/env python

import unittest
import datetime

from mock import patch, MagicMock

import composer.config as config
from composer.backend import FilesystemPlanner, FilesystemTasklist
from composer.timeperiod import Day, Week, Month, Quarter, Year, is_weekend

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
    """check exceptions if file exists (e.g. running twice). Check symlinks
    are updated
    """

    pass


class PlannerInvalidStateFailGracefullyTester(unittest.TestCase):
    """check that if any needed files are missing it fails gracefully with
    exception and without making changes
    """

    pass


# TODO: use (merge into as needed) planner fixture instead of this base class
class PlannerIntegrationTest(unittest.TestCase):
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
        "THIS QUARTER:\n"
        "\n"
        "THIS YEAR:\n"
        "\n"
        "SOMEDAY:\n"
    )

    yeartemplate = (
        "= 2012 =\n"
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
        "[ ] get groceries\n"
        "[\\] do dishes\n"
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
        "[ ] get groceries\n"
        "[\\] do dishes\n"
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
        "[ ] get groceries\n"
        "[\\] do dishes\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule\n"
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
        tasklist = FilesystemTasklist()
        tasklist.file = StringIO(self.tasklist)
        self.planner.tasklist = tasklist
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
        self.planner.week_theme = ''
        self.planner.location = ''
        self.planner.next_day_planner = FilesystemPlanner()
        self.planner.agenda_reviewed = Year
        mock_get_log = MagicMock()
        mock_get_log.return_value = True
        self.planner.get_log = mock_get_log


class PlannerAdvanceTester(PlannerIntegrationTest):

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
        "\t\t    January 2013      \n"
        "\t\tSu Mo Tu We Th Fr Sa  \n"
        "\t\t       1  2  3  4  5  \n"
        "\t\t 6  7  8  9 10 11 12  \n"
        "\t\t13 14 15 16 17 18 19  \n"
        "\t\t20 21 22 23 24 25 26  \n"
        "\t\t27 28 29 30 31        \n"
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

    yearadvance_yeartemplate_jump = (
        "= 2013 =\n"
        "\n"
        "\t* [[Q3 2013]]\n"
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

    yearadvance_quartertemplate_jump = (
        "= Q3 2013 =\n"
        "\n"
        "\t* [[Month of August, 2013]]\n"
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

    yearadvance_monthtemplate_jump = (
        "= AUGUST 2013 =\n"
        "\n"
        "\t\t    August 2013       \n"
        "\t\tSu Mo Tu We Th Fr Sa  \n"
        "\t\t             1  2  3  \n"
        "\t\t 4  5  6  7  8  9 10  \n"
        "\t\t11 12 13 14 15 16 17  \n"
        "\t\t18 19 20 21 22 23 24  \n"
        "\t\t25 26 27 28 29 30 31  \n"
        "\n"
        "\t* [[Week of August 18, 2013]]\n"
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

    yearadvance_weektemplate_jump = (
        "= WEEK OF AUGUST 18, 2013 =\n"
        "\n"
        "\t* [[August 20, 2013]]\n"
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

    quarteradvance_yeartemplate = (
        "= 2012 =\n"
        "\t* [[Q4 2012]]\n"
        "\t* [[Q3 2012]]\n"
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

    quarteradvance_quartertemplate = PlannerIntegrationTest.quartertemplate

    quarteradvance_monthtemplate = (
        "= OCTOBER 2012 =\n"
        "\n"
        "\t\t    October 2012      \n"
        "\t\tSu Mo Tu We Th Fr Sa  \n"
        "\t\t    1  2  3  4  5  6  \n"
        "\t\t 7  8  9 10 11 12 13  \n"
        "\t\t14 15 16 17 18 19 20  \n"
        "\t\t21 22 23 24 25 26 27  \n"
        "\t\t28 29 30 31           \n"
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

    monthadvance_quartertemplate = (
        "= Q4 2012 =\n"
        "\n"
        "\t* [[Month of November, 2012]]\n"
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

    monthadvance_monthtemplate = (
        "= NOVEMBER 2012 =\n"
        "\n"
        "\t\t   November 2012      \n"
        "\t\tSu Mo Tu We Th Fr Sa  \n"
        "\t\t             1  2  3  \n"
        "\t\t 4  5  6  7  8  9 10  \n"
        "\t\t11 12 13 14 15 16 17  \n"
        "\t\t18 19 20 21 22 23 24  \n"
        "\t\t25 26 27 28 29 30     \n"
        "\n"
        "\t* [[Week of November 1, 2012]]\n"
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

    monthadvance_weektemplate = (
        "= WEEK OF NOVEMBER 1, 2012 =\n"
        "\n"
        "\t* [[November 1, 2012]]\n"
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

    @patch('composer.backend.filesystem.base.full_file_path')
    @patch('composer.backend.filesystem.base.read_file')
    @patch('composer.backend.filesystem.base.string_to_date')
    def test_advance_propagates_tasklist(
        self, mock_get_date, mock_read_file, mock_file_path
    ):
        today = datetime.date(2012, 12, 5)
        mock_get_date.return_value = (today, Day)
        mock_file_path.return_value = ''
        mock_read_file.return_value = StringIO('')
        next_day = today + datetime.timedelta(days=1)

        mock_next_day = MagicMock()
        mock_next_day.return_value = next_day
        self.planner.next_day = mock_next_day

        self.planner.date = today
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]

        _, next_day_planner = self.planner.advance()

        assert (
            next_day_planner.tasklist.file.getvalue()
            == self.planner.tasklist.file.getvalue()
        )

    def _day_template(self, for_date):
        (date, day, month, year) = (
            for_date.day,
            for_date.strftime('%A'),
            for_date.strftime('%B'),
            for_date.year,
        )
        daytemplate = ""
        daytemplate += "= %s %s %d, %d =\n" % (
            day.upper(),
            month[:3].upper(),
            date,
            year,
        )
        daytemplate += "\n"
        dailythemes = self.daythemes.lower()
        theme = dailythemes[dailythemes.index(day.lower()) :]
        theme = theme[theme.index(':') :].strip(': ')
        theme = theme[: theme.index('\n')].strip().upper()
        theme = "*" + theme + "*"
        if len(theme) > 2:
            daytemplate += "Theme: %s\n" % theme
            daytemplate += "\n"
        if is_weekend(for_date):
            daytemplate += self.default_weekendtemplate
        else:
            daytemplate += self.default_weekdaytemplate
        return daytemplate

    @patch('composer.backend.filesystem.base.read_file')
    @patch('composer.backend.filesystem.base.full_file_path')
    @patch('composer.backend.filesystem.base.string_to_date')
    def test_advance_year(self, mock_get_date, mock_file_path, mock_read_file):
        """Check that planner advance returns the correct new year, quarter,
        month, week, and day templates when advancing year
        """
        today = datetime.date(2012, 12, 31)
        mock_get_date.return_value = (today, Day)
        mock_file_path.return_value = ''
        mock_read_file.return_value = StringIO('')
        next_day = today + datetime.timedelta(days=1)
        daytemplate = self._day_template(next_day)
        self.planner.date = today
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]

        self.planner.advance()

        self.assertEqual(
            self.planner.next_day_planner.yearfile.read(),
            self.yearadvance_yeartemplate,
        )
        self.assertEqual(
            self.planner.next_day_planner.quarterfile.read(),
            self.yearadvance_quartertemplate,
        )
        self.assertEqual(
            self.planner.next_day_planner.monthfile.read(),
            self.yearadvance_monthtemplate,
        )
        self.assertEqual(
            self.planner.next_day_planner.weekfile.read(),
            self.yearadvance_weektemplate,
        )
        self.assertEqual(
            self.planner.next_day_planner.dayfile.read(), daytemplate
        )

    @patch('composer.backend.filesystem.base.read_file')
    @patch('composer.backend.filesystem.base.full_file_path')
    @patch('composer.backend.filesystem.base.string_to_date')
    def test_advance_year_with_jump(
        self, mock_get_date, mock_file_path, mock_read_file
    ):
        """Check that planner advance returns the correct new year, quarter,
        month, week, and day templates when advancing year as part of a jump
        """
        today = datetime.date(2012, 12, 31)
        mock_get_date.return_value = (today, Day)
        mock_file_path.return_value = ''
        mock_read_file.return_value = StringIO('')
        next_day = datetime.date(2013, 8, 20)
        daytemplate = self._day_template(next_day)
        self.planner.get_log.return_value = False
        self.planner.date = today
        self.planner.jump_to_date = next_day
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]

        self.planner.advance()

        self.assertEqual(
            self.planner.next_day_planner.yearfile.read(),
            self.yearadvance_yeartemplate_jump,
        )
        self.assertEqual(
            self.planner.next_day_planner.quarterfile.read(),
            self.yearadvance_quartertemplate_jump,
        )
        self.assertEqual(
            self.planner.next_day_planner.monthfile.read(),
            self.yearadvance_monthtemplate_jump,
        )
        self.assertEqual(
            self.planner.next_day_planner.weekfile.read(),
            self.yearadvance_weektemplate_jump,
        )
        self.assertEqual(
            self.planner.next_day_planner.dayfile.read(), daytemplate
        )

    @patch('composer.backend.filesystem.base.read_file')
    @patch('composer.backend.filesystem.base.full_file_path')
    @patch('composer.backend.filesystem.base.string_to_date')
    def test_advance_quarter(
        self, mock_get_date, mock_file_path, mock_read_file
    ):
        """Check that planner advance returns the correct new quarter, month,
        week, and day templates when advancing quarter
        """
        today = datetime.date(2012, 9, 30)
        self.planner.date = today
        mock_get_date.return_value = (today, Day)
        mock_file_path.return_value = ''
        mock_read_file.return_value = StringIO('')
        next_day = today + datetime.timedelta(days=1)
        daytemplate = self._day_template(next_day)
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.advance()
        self.assertEqual(
            self.planner.yearfile.read(), self.quarteradvance_yeartemplate
        )
        self.assertEqual(
            self.planner.next_day_planner.quarterfile.read(),
            self.quarteradvance_quartertemplate,
        )
        self.assertEqual(
            self.planner.next_day_planner.monthfile.read(),
            self.quarteradvance_monthtemplate,
        )
        self.assertEqual(
            self.planner.next_day_planner.weekfile.read(),
            self.quarteradvance_weektemplate,
        )
        self.assertEqual(
            self.planner.next_day_planner.dayfile.read(), daytemplate
        )

    @patch('composer.backend.filesystem.base.read_file')
    @patch('composer.backend.filesystem.base.full_file_path')
    @patch('composer.backend.filesystem.base.string_to_date')
    def test_advance_month(
        self, mock_get_date, mock_file_path, mock_read_file
    ):
        """Check that planner advance returns the correct new month, week, and
        day templates when advancing month
        """
        today = datetime.date(2012, 10, 31)
        mock_get_date.return_value = (today, Day)
        mock_file_path.return_value = ''
        mock_read_file.return_value = StringIO('')
        next_day = today + datetime.timedelta(days=1)
        daytemplate = self._day_template(next_day)
        self.planner.date = today
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.advance()
        self.assertEqual(
            self.planner.quarterfile.read(), self.monthadvance_quartertemplate
        )
        self.assertEqual(
            self.planner.next_day_planner.monthfile.read(),
            self.monthadvance_monthtemplate,
        )
        self.assertEqual(
            self.planner.next_day_planner.weekfile.read(),
            self.monthadvance_weektemplate,
        )
        self.assertEqual(
            self.planner.next_day_planner.dayfile.read(), daytemplate
        )

    @patch('composer.backend.filesystem.base.read_file')
    @patch('composer.backend.filesystem.base.full_file_path')
    @patch('composer.backend.filesystem.base.string_to_date')
    def test_advance_week(self, mock_get_date, mock_file_path, mock_read_file):
        """Check that planner advance returns the correct new week and day
        templates, and updates the existing month template correctly, when
        advancing week
        """
        today = datetime.date(2012, 12, 8)
        mock_get_date.return_value = (today, Day)
        mock_file_path.return_value = ''
        mock_read_file.return_value = StringIO('')
        next_day = today + datetime.timedelta(days=1)
        daytemplate = self._day_template(next_day)
        self.planner.date = today
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.advance()
        self.assertEqual(
            self.planner.monthfile.read(), self.weekadvance_monthtemplate
        )
        self.assertEqual(
            self.planner.next_day_planner.weekfile.read(),
            self.weekadvance_weektemplate,
        )
        self.assertEqual(
            self.planner.next_day_planner.dayfile.read(), daytemplate
        )

    @patch('composer.backend.filesystem.base.read_file')
    @patch('composer.backend.filesystem.base.full_file_path')
    @patch('composer.backend.filesystem.base.string_to_date')
    def test_advance_day(self, mock_get_date, mock_file_path, mock_read_file):
        """Check that planner advance returns the correct new day template,
        and updates the existing week template, when advancing day
        """
        today = datetime.date(2012, 12, 5)
        mock_get_date.return_value = (today, Day)
        mock_file_path.return_value = ''
        mock_read_file.return_value = StringIO('')
        next_day = today + datetime.timedelta(days=1)
        daytemplate = self._day_template(next_day)
        self.planner.date = today
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.advance()
        self.assertEqual(
            self.planner.weekfile.read(), self.dayadvance_weektemplate
        )
        self.assertEqual(
            self.planner.next_day_planner.dayfile.read(), daytemplate
        )


class TestAgendaCascade(PlannerIntegrationTest):
    yeartemplate_agendaupdated_completed = (
        "= 2012 =\n"
        "\t* [[Q3 2012]]\n"
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

    yeartemplate_agendaupdated_all = (
        "= 2012 =\n"
        "\t* [[Q3 2012]]\n"
        "\n"
        "CHECKPOINTS:\n"
        "[ ] Q1 - []\n[ ] Q2 - []\n[ ] Q3 - []\n[ ] Q4 - []\n"
        "\n"
        "AGENDA:\n"
        "[x] take out trash\n"
        "[x] floss\n"
        "[ ] get groceries\n"
        "[\\] do dishes\n"
        "\n"
        "YEARLYs:\n"
        "[ ] 1 significant life achievement\n"
        "\n"
        "NOTES:\n"
        "\n\n"
        "TIME SPENT ON PLANNER: "
    )

    quartertemplate_agendaupdated_completed = (
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

    quartertemplate_agendaupdated_all = (
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
        "[ ] get groceries\n"
        "[\\] do dishes\n"
        "\n"
        "QUARTERLYs:\n"
        "[ ] 1 major research achievement\n[ ] 1 major coding achievement\n[ ] 1 unique achievement\n[ ] update financials\n"
        "\n"
        "NOTES:\n"
        "\n\n"
        "TIME SPENT ON PLANNER: "
    )

    monthtemplate_agendaupdated_completed = (
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

    monthtemplate_agendaupdated_all = (
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
        "[ ] get groceries\n"
        "[\\] do dishes\n"
        "\n"
        "MONTHLYs:\n"
        "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
        "\n"
        "NOTES:\n"
        "\n\n"
        "TIME SPENT ON PLANNER: "
    )

    weektemplate_agendaupdated_completed = (
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

    weektemplate_agendaupdated_all = (
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
        "[ ] get groceries\n"
        "[\\] do dishes\n"
        "\n"
        "WEEKLYs:\n"
        "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
        "\n"
        "NOTES:\n"
        "\n\n"
        "TIME SPENT ON PLANNER: "
    )

    def test_day_to_week(self):
        """Check that, on day advance, current day's agenda is appended to the
        current week
        """
        current_day = datetime.date(2012, 12, 5)
        self.planner.date = current_day
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.cascade_agenda(Day)
        self.assertEqual(
            self.planner.weekfile.read(),
            self.weektemplate_agendaupdated_completed,
        )

    def test_month_for_week_to_month(self):
        """Check that, on week advance, current week's agenda is appended to
        the current month
        """
        current_day = datetime.date(2012, 12, 5)
        self.planner.date = current_day
        self.planner.weekfile = StringIO(self.weektemplate_agendaupdated_all)
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.cascade_agenda(Week)
        self.assertEqual(
            self.planner.monthfile.read(),
            self.monthtemplate_agendaupdated_completed,
        )

    def test_week_for_week_to_month(self):
        """Check that, on week advance, current week's agenda is appended to
        the current month
        """
        current_day = datetime.date(2012, 12, 5)
        self.planner.date = current_day
        self.planner.weekfile = StringIO(
            self.weektemplate_agendaupdated_completed
        )
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.cascade_agenda(Week)
        self.assertEqual(
            self.planner.weekfile.read(), self.weektemplate_agendaupdated_all
        )

    def test_quarter_for_month_to_quarter(self):
        """Check that, on month advance, current month's agenda is appended to
        the current quarter
        """
        current_day = datetime.date(2012, 12, 5)
        self.planner.date = current_day
        self.planner.monthfile = StringIO(self.monthtemplate_agendaupdated_all)
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.cascade_agenda(Month)
        self.assertEqual(
            self.planner.quarterfile.read(),
            self.quartertemplate_agendaupdated_completed,
        )

    def test_month_for_month_to_quarter(self):
        """Check that, on month advance, current month's agenda is appended to
        the current quarter
        """
        current_day = datetime.date(2012, 12, 5)
        self.planner.date = current_day
        self.planner.weekfile = StringIO(self.weektemplate_agendaupdated_all)
        self.planner.monthfile = StringIO(
            self.monthtemplate_agendaupdated_completed
        )
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.cascade_agenda(Month)
        self.assertEqual(
            self.planner.monthfile.read(), self.monthtemplate_agendaupdated_all
        )

    def test_year_for_quarter_to_year(self):
        """Check that, on quarter advance, current quarter's agenda is
        appended to the current year
        """
        current_day = datetime.date(2012, 9, 30)
        self.planner.date = current_day
        self.planner.quarterfile = StringIO(
            self.quartertemplate_agendaupdated_all
        )
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.cascade_agenda(Quarter)
        self.assertEqual(
            self.planner.yearfile.read(),
            self.yeartemplate_agendaupdated_completed,
        )

    def test_quarter_for_quarter_to_year(self):
        """Check that, on quarter advance, current quarter's agenda is
        appended to the current year
        """
        current_day = datetime.date(2012, 9, 30)
        self.planner.date = current_day
        self.planner.monthfile = StringIO(self.monthtemplate_agendaupdated_all)
        self.planner.quarterfile = StringIO(
            self.quartertemplate_agendaupdated_completed
        )
        self.planner.logfile_completion_checking = config.LOGFILE_CHECKING[
            'LAX'
        ]
        self.planner.cascade_agenda(Quarter)
        self.assertEqual(
            self.planner.quarterfile.read(),
            self.quartertemplate_agendaupdated_all,
        )


if __name__ == '__main__':
    unittest.main()
