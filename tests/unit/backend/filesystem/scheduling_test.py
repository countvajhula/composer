import datetime
import unittest
import pytest

from mock import patch

from composer.backend import FilesystemPlanner, FilesystemTasklist
from composer.backend.filesystem.scheduling import (
    standardize_entry_date,
    get_due_date,
    string_to_date,
    is_task_due,
    date_to_string,
)
from composer.timeperiod import Day, Week, Month, Quarter, Year, Eternity
from composer.errors import BlockedTaskNotScheduledError, InvalidDateError

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


class TestStandardizeEntryDate(object):
    def test_already_standard(self):
        date = datetime.datetime(2012, 12, 12)
        entry = "[o] do this [$DECEMBER 12, 2012$]"
        expected = entry
        with patch(
            "composer.backend.filesystem.scheduling" ".string_to_date"
        ) as mock_get_date:
            mock_get_date.return_value = (date, Day)
            standard = standardize_entry_date(entry)
        assert standard == expected

    def test_nonstandard(self):
        date = datetime.datetime(2012, 12, 12)
        entry = "[o] do this [$12 DECEMBER, 2012$]"
        expected = "[o] do this [$DECEMBER 12, 2012$]"
        with patch(
            "composer.backend.filesystem.scheduling" ".string_to_date"
        ) as mock_get_date:
            mock_get_date.return_value = (date, Day)
            standard = standardize_entry_date(entry)
        assert standard == expected

    def test_retains_subtasks(self):
        date = datetime.datetime(2012, 12, 12)
        entry = (
            "[o] do this [$12 DECEMBER, 2012$]\n"
            "\t[\\] first thing\n"
            "\t[ ] second thing\n"
        )
        expected = (
            "[o] do this [$DECEMBER 12, 2012$]\n"
            "\t[\\] first thing\n"
            "\t[ ] second thing\n"
        )
        with patch(
            "composer.backend.filesystem.scheduling" ".string_to_date"
        ) as mock_get_date:
            mock_get_date.return_value = (date, Day)
            standard = standardize_entry_date(entry)
        assert standard == expected


class TestStringToDate(object):
    def test_format1(self):
        date_string = "OCTOBER 12, 2013"
        expected_date = datetime.date(2013, 10, 12)
        expected_period = Day
        date, period = string_to_date(date_string)
        assert date == expected_date
        assert period == expected_period

    def test_format2(self):
        date_string = "12 OCTOBER, 2013"
        expected_date = datetime.date(2013, 10, 12)
        expected_period = Day
        date, period = string_to_date(date_string)
        assert date == expected_date
        assert period == expected_period

    def test_format3(self):
        today = datetime.date(2013, 6, 1)
        date_string = "OCTOBER 12"
        expected_date = datetime.date(2013, 10, 12)
        expected_period = Day
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format4(self):
        today = datetime.date(2013, 6, 1)
        date_string = "12 OCTOBER"
        expected_date = datetime.date(2013, 10, 12)
        expected_period = Day
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    @pytest.mark.parametrize(
        "date_string, expected_date",
        [
            # format 5
            ("WEEK OF OCTOBER 13, 2013", datetime.date(2013, 10, 13)),
            ("WEEK OF OCTOBER 15, 2013", datetime.date(2013, 10, 13)),
            # start of week not on Sunday
            ("WEEK OF MAY 2, 2013", datetime.date(2013, 5, 1)),
            # format 6
            ("WEEK OF 13 OCTOBER, 2013", datetime.date(2013, 10, 13)),
            ("WEEK OF 15 OCTOBER, 2013", datetime.date(2013, 10, 13)),
            # start of week not on Sunday
            ("WEEK OF 2 MAY, 2013", datetime.date(2013, 5, 1)),
            # format 7
            ("WEEK OF OCTOBER 13", datetime.date(2013, 10, 13)),
            ("WEEK OF OCTOBER 15", datetime.date(2013, 10, 13)),
            # start of week not on Sunday
            ("WEEK OF MAY 2", datetime.date(2013, 5, 1)),
            # format 8
            ("WEEK OF 13 OCTOBER", datetime.date(2013, 10, 13)),
            ("WEEK OF 15 OCTOBER", datetime.date(2013, 10, 13)),
            # start of week not on Sunday
            ("WEEK OF 2 MAY", datetime.date(2013, 5, 1)),
        ],
    )
    def test_format5_6_7_8(self, date_string, expected_date):
        # TODO: should week boundary checking be handled by a higher-level
        # function?
        today = datetime.date(2013, 4, 1)
        expected_period = Week
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format9(self):
        today = datetime.date(2013, 6, 1)
        date_string = "OCTOBER 2013"
        expected_date = datetime.date(2013, 10, 1)
        expected_period = Month
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format10(self):
        today = datetime.date(2013, 6, 1)
        date_string = "OCTOBER"
        expected_date = datetime.date(2013, 10, 1)
        expected_period = Month
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format11(self):
        today = datetime.date(2013, 6, 1)
        date_string = "10/14/2013"
        expected_date = datetime.date(2013, 10, 14)
        expected_period = Day
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format12(self):
        today = datetime.date(2013, 6, 1)
        date_string = "10-14-2013"
        expected_date = datetime.date(2013, 10, 14)
        expected_period = Day
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format13(self):
        today = datetime.date(2013, 6, 1)
        date_string = "TOMORROW"
        expected_date = datetime.date(2013, 6, 2)
        expected_period = Day
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    @pytest.mark.parametrize(
        "today, expected_date",
        [
            (datetime.date(2013, 10, 9), datetime.date(2013, 10, 13)),
            # start of week not on Sunday
            (datetime.date(2013, 4, 28), datetime.date(2013, 5, 1)),
        ],
    )
    def test_format14(self, today, expected_date):
        date_string = "NEXT WEEK"
        expected_period = Week
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format15(self):
        today = datetime.date(2013, 6, 1)
        date_string = "NEXT MONTH"
        expected_date = datetime.date(2013, 7, 1)
        expected_period = Month
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format16(self):
        today = datetime.date(2013, 10, 10)
        date_string = "TUESDAY"
        expected_date = datetime.date(2013, 10, 15)
        expected_period = Day
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format17(self):
        today = datetime.date(2013, 10, 10)
        date_string = "TUE"
        expected_date = datetime.date(2013, 10, 15)
        expected_period = Day
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format18(self):
        today = datetime.date(2013, 10, 10)
        date_string = "Q4 2013"
        expected_date = datetime.date(2013, 10, 1)
        expected_period = Quarter
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format19(self):
        today = datetime.date(2012, 10, 10)
        date_string = "NEXT YEAR"
        expected_date = datetime.date(2013, 1, 1)
        expected_period = Year
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format20(self):
        today = datetime.date(2012, 10, 10)
        date_string = "2013"
        expected_date = datetime.date(2013, 1, 1)
        expected_period = Year
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    @pytest.mark.parametrize(
        "today, expected_date",
        [
            (datetime.date(2013, 10, 9), datetime.date(2013, 10, 12)),
            # start of weekend
            (datetime.date(2013, 10, 12), datetime.date(2013, 10, 12)),
            # start of week
            (datetime.date(2013, 10, 13), datetime.date(2013, 10, 19)),
        ],
    )
    def test_format21(self, today, expected_date):
        date_string = "THIS WEEKEND"
        expected_period = Day
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    @pytest.mark.parametrize(
        "today, expected_date",
        [
            (datetime.date(2013, 10, 9), datetime.date(2013, 10, 19)),
            # start of weekend
            (datetime.date(2013, 10, 12), datetime.date(2013, 10, 19)),
            # start of week
            (datetime.date(2013, 10, 13), datetime.date(2013, 10, 26)),
        ],
    )
    def test_format22(self, today, expected_date):
        date_string = "NEXT WEEKEND"
        expected_period = Day
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    @pytest.mark.parametrize(
        "today, expected_date",
        [
            (datetime.date(2012, 7, 12), datetime.date(2012, 10, 1)),
            (datetime.date(2012, 8, 12), datetime.date(2012, 10, 1)),
            (datetime.date(2012, 9, 12), datetime.date(2012, 10, 1)),
            (datetime.date(2012, 10, 12), datetime.date(2013, 1, 1)),
        ],
    )
    def test_format23(self, today, expected_date):
        date_string = "NEXT QUARTER"
        expected_period = Quarter
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    @pytest.mark.parametrize(
        "today, expected_date",
        [
            (datetime.date(2012, 7, 12), datetime.date(2012, 10, 1)),
            (datetime.date(2012, 8, 12), datetime.date(2012, 10, 1)),
            (datetime.date(2012, 9, 12), datetime.date(2012, 10, 1)),
            (datetime.date(2012, 10, 12), datetime.date(2013, 10, 1)),
        ],
    )
    def test_format24(self, today, expected_date):
        date_string = "Q4"
        expected_period = Quarter
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format25(self):
        today = datetime.date(2013, 6, 1)
        date_string = "DAY AFTER TOMORROW"
        expected_date = datetime.date(2013, 6, 3)
        expected_period = Day
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period

    def test_format26(self):
        today = datetime.date(2013, 6, 1)
        date_string = "SOMEDAY"
        expected_date = datetime.date(9999, 12, 12)
        expected_period = Eternity
        date, period = string_to_date(date_string, reference_date=today)
        assert date == expected_date
        assert period == expected_period


class TestDateToString(object):
    def test_day(self):
        today = datetime.date(2012, 10, 14)
        expected = "OCTOBER 14, 2012"
        result = date_to_string(today, Day)
        assert result == expected

    def test_week(self):
        today = datetime.date(2012, 10, 14)
        expected = "WEEK OF OCTOBER 14, 2012"
        result = date_to_string(today, Week)
        assert result == expected

    def test_month(self):
        today = datetime.date(2012, 10, 14)
        expected = "OCTOBER 2012"
        result = date_to_string(today, Month)
        assert result == expected

    def test_quarter(self):
        today = datetime.date(2012, 10, 14)
        expected = "Q4 2012"
        result = date_to_string(today, Quarter)
        assert result == expected

    def test_year(self):
        today = datetime.date(2012, 10, 14)
        expected = "2012"
        result = date_to_string(today, Year)
        assert result == expected

    def test_eternity(self):
        today = datetime.date(2012, 10, 14)
        expected = "SOMEDAY"
        result = date_to_string(today, Eternity)
        assert result == expected


class TestDueDate(object):
    def test_day_format(self):
        task = "[o] something [$OCTOBER 12, 2013$]"
        expected = datetime.date(2013, 10, 12)
        result, _ = get_due_date(task)
        assert result == expected

    def test_week_format(self):
        task = "[o] something [$WEEK OF OCTOBER 13, 2013$]"
        expected = datetime.date(2013, 10, 13)
        result, _ = get_due_date(task)
        assert result == expected

    def test_month_format(self):
        task = "[o] something [$OCTOBER 2013$]"
        expected = datetime.date(2013, 10, 1)
        result, _ = get_due_date(task)
        assert result == expected

    def test_quarter_format(self):
        task = "[o] something [$Q4 2013$]"
        expected = datetime.date(2013, 10, 1)
        result, _ = get_due_date(task)
        assert result == expected

    def test_year_format(self):
        task = "[o] something [$2013$]"
        expected = datetime.date(2013, 1, 1)
        result, _ = get_due_date(task)
        assert result == expected

    def test_eternity_format(self):
        task = "[o] something [$SOMEDAY$]"
        expected = datetime.date(9999, 12, 12)
        result, _ = get_due_date(task)
        assert result == expected


class TestIsTaskDue(object):
    def test_due_date_in_past(self):
        today = datetime.date(2013, 10, 14)
        task = "[o] something [$OCTOBER 13, 2013$]"
        assert is_task_due(task, for_day=today)

    def test_on_due_date(self):
        today = datetime.date(2013, 10, 14)
        task = "[o] something [$OCTOBER 14, 2013$]"
        assert is_task_due(task, for_day=today)

    def test_due_date_in_future(self):
        today = datetime.date(2013, 10, 14)
        task = "[o] something [$OCTOBER 15, 2013$]"
        assert not is_task_due(task, for_day=today)


class PlannerTaskSchedulingTester(unittest.TestCase):
    """ Check the logfile -> tasklist flow. This adds any newly scheduled tasks
    in the logfile to the tasklist in the appropriate section.
    """

    # TODO: test when week of is set at an actual sunday, and at 1st of month
    # TODO: "first/second/third/fourth week of month"
    # TODO: "next week/month/year"

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

    tasklist_agenda = (
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
        "[o] i'm waitin on you! [$DECEMBER 20, 2012$]\n"
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
        "[o] still waitin on you [$JANUARY 14, 2013$]\n"
    )

    tasklist_scheduled_formats1to4and11to13 = tasklist_agenda

    tasklist_scheduled_formats5to8and14 = (
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
        "[o] i'm waitin on you! [$WEEK OF DECEMBER 16, 2012$]\n"
        "\n"
        "THIS QUARTER:\n"
        "\n"
        "THIS YEAR:\n"
        "\n"
        "SOMEDAY:\n"
        "[o] still waitin on you [$WEEK OF JANUARY 13, 2013$]\n"
    )

    tasklist_scheduled_formats9to10 = (
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
        "[o] i'm waitin on you! [$DECEMBER 2012$]\n"
        "\n"
        "THIS YEAR:\n"
        "\n"
        "SOMEDAY:\n"
        "[o] still waitin on you [$JANUARY 2013$]\n"
    )

    tasklist_scheduled_format15 = (
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
        "[o] still waitin on you [$JANUARY 2013$]\n"
    )

    tasklist_scheduled_formats16and17 = (
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
        "[o] i'm waitin till tuesday! [$DECEMBER 4, 2012$]\n"
        "[o] i'm waitin till wednesday! [$DECEMBER 5, 2012$]\n"
        "[o] i'm waitin till thursday! [$DECEMBER 6, 2012$]\n"
        "[o] i'm waitin till friday! [$DECEMBER 7, 2012$]\n"
        "[o] i'm waitin till saturday! [$DECEMBER 8, 2012$]\n"
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
        "[o] i'm waitin till sunday! [$DECEMBER 9, 2012$]\n"
        "[o] i'm waitin till monday! [$DECEMBER 10, 2012$]\n"
        "\n"
        "THIS QUARTER:\n"
        "\n"
        "THIS YEAR:\n"
        "\n"
        "SOMEDAY:\n"
    )

    tasklist_scheduled_format26 = (
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
        "[o] still waitin on you [$SOMEDAY$]\n"
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

    quartertemplate = (
        "= Q4 2012 =\n"
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
        "TIME SPENT ON PLANNER: "
    )

    monthtemplate = (
        "= DECEMBER 2012 =\n"
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
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[x] take out trash\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format1 = daytemplate_scheduled

    daytemplate_scheduled_format2 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format3 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format4 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format5 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[o] i'm waitin on you! [$WEEK OF DECEMBER 16, 2012$]\n"
        "[o] still waitin on you [$WEEK OF JANUARY 13, 2013$]\n"
        "[x] take out trash\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format6 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[o] i'm waitin on you! [$WEEK OF 16 DECEMBER, 2012$]\n"
        "[o] still waitin on you [$WEEK OF 13 JANUARY, 2013$]\n"
        "[x] take out trash\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format7 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[o] i'm waitin on you! [$WEEK OF DECEMBER 16$]\n"
        "[o] still waitin on you [$WEEK OF JANUARY 13$]\n"
        "[x] take out trash\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format8 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[o] i'm waitin on you! [$WEEK OF 16 DECEMBER$]\n"
        "[o] still waitin on you [$WEEK OF 13 JANUARY$]\n"
        "[x] take out trash\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format9 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[o] i'm waitin on you! [$DECEMBER 2012$]\n"
        "[o] still waitin on you [$JANUARY, 2013$]\n"
        "[x] take out trash\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format10 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format10_lowercase = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[o] i'm waitin on you! [$December$]\n"
        "[o] still waitin on you [$january$]\n"
        "[x] take out trash\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format11 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format12 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format13 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format14 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format15 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[o] still waitin on you [$NEXT MONTH$]\n"
        "[x] take out trash\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format16 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format17 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_noscheduledate = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[o] i'm waitin on you!\n"
        "[x] take out trash\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: 15 mins"
    )

    daytemplate_scheduled_format26 = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[o] still waitin on you [$SOMEDAY$]\n"
        "[x] take out trash\n"
        "\n"
        "DAILYs:\n"
        "[ ] 40 mins gym\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: 15 mins"
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
        self.planner.date = datetime.date(2012, 12, 19)
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
        self.planner.next_day_planner = FilesystemPlanner()

    def test_agenda_scheduled_tasks_are_scheduled(self):
        """ Check that scheduling tasks pulls all scheduled tasks from today's Agenda
        into the SCHEDULED section of the tasklist """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(), self.tasklist_agenda
        )

    def test_scheduled_task_without_date_raises_exception(self):
        """ Check that if a task is marked as scheduled but no date is provided, that
        an exception is thrown """
        self.planner.dayfile = StringIO(self.daytemplate_noscheduledate)
        self.assertRaises(
            BlockedTaskNotScheduledError, self.planner.schedule_tasks
        )

    def test_scheduled_task_with_date_in_the_past_raises_exception(self):
        """ Check that if a task is marked as scheduled but a date in the past
        is provided, that an exception is thrown """
        self.planner.date = datetime.date(2012, 12, 20)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled)
        self.assertRaises(InvalidDateError, self.planner.schedule_tasks)

    def test_schedule_date_format1(self):
        """ Check that the format MONTH DD, YYYY works (w optional space or comma or both) """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format1)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format2(self):
        """ Check that the format DD MONTH, YYYY works (w optional space or comma or both) """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format2)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format3(self):
        """ Check that the format MONTH DD works """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format3)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format4(self):
        """ Check that the format DD MONTH works """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format4)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format5(self):
        """ Check that the format WEEK OF MONTH DD, YYYY works (w optional space or comma or both) """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format5)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats5to8and14,
        )

    def test_schedule_date_format6(self):
        """ Check that the format WEEK OF DD MONTH, YYYY works (w optional space or comma or both) """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format6)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats5to8and14,
        )

    def test_schedule_date_format7(self):
        """ Check that the format WEEK OF MONTH DD works """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format7)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats5to8and14,
        )

    def test_schedule_date_format8(self):
        """ Check that the format WEEK OF DD MONTH works """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format8)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats5to8and14,
        )

    def test_schedule_date_format9(self):
        """ Check that the format MONTH YYYY works (w optional space or comma or both) """
        self.planner.date = datetime.date(2012, 11, 4)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format9)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats9to10,
        )

    def test_schedule_date_format10(self):
        """ Check that the format MONTH works """
        self.planner.date = datetime.date(2012, 11, 4)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format10)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats9to10,
        )

    def test_schedule_date_format11(self):
        """ Check that the format MM/DD/YYYY works """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format11)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format12(self):
        """ Check that the format MM-DD-YYYY works """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format12)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format13(self):
        """ Check that the format TOMORROW works """
        self.planner.date = datetime.date(2012, 12, 19)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format13)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format14(self):
        """ Check that the format NEXT WEEK works """
        self.planner.date = datetime.date(2012, 12, 10)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format14)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats5to8and14,
        )

    def test_schedule_date_format15(self):
        """ Check that the format NEXT MONTH works """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format15)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(), self.tasklist_scheduled_format15
        )

    def test_schedule_date_format16(self):
        """ Check that the format <DOW> works """
        self.planner.date = datetime.date(2012, 12, 3)  # monday
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format16)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats16and17,
        )

    def test_schedule_date_format17(self):
        """ Check that the format <DOW> (abbrv.) works """
        self.planner.date = datetime.date(2012, 12, 3)  # monday
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format17)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats16and17,
        )

    def test_schedule_date_format26(self):
        """ Check that the format SOMEDAY works """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format26)
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(), self.tasklist_scheduled_format26
        )

    def test_schedule_date_is_case_insensitive(self):
        """ Check that schedule date is case insensitive, by testing a lowercase month """
        self.planner.date = datetime.date(2012, 11, 4)
        self.planner.dayfile = StringIO(
            self.daytemplate_scheduled_format10_lowercase
        )
        self.planner.schedule_tasks()
        self.assertEqual(
            self.planner.tasklist.file.read(),
            self.tasklist_scheduled_formats9to10,
        )
