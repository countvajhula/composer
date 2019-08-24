import datetime
import unittest

import composer.config as config
import composer.backend.filesystem.templates as templates
from composer.time import Day

from .fixtures import PlannerMock

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


class PlannerAgendaConstructionTester(unittest.TestCase):

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

    tasklist_tomorrow = (
        "TOMORROW:\n"
        "[ ] contact dude\n"
        "[\\] make X\n"
        "[o] call somebody [$DECEMBER 12, 2012$]\n"
        "[o] apply for something [DECEMBER 26, 2012]\n"
        "[ ] finish project\n"
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

    tasklist_somescheduled = (
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
        "[o] this task is for some day but probably not the day you're looking for [$DECEMBER 15, 2012$]\n"
        "[o] this task is def not the one you need to do [$DECEMBER 19, 2012$]\n"
    )

    tasklist_scheduledfortomorrow = (
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
        "[o] this is an old task that should have been done long ago! [$DECEMBER 3, 2012$]\n"
        "[o] this task could be the one you need to do! [$DECEMBER 10, 2012$]\n"
        "[o] here's one that should be pulled up [$WEEK OF DECEMBER 9, 2012$]\n"
        "[o] here's one that shouldn't be pulled up [$WEEK OF DECEMBER 16, 2012$]\n"
    )

    tasklist_scheduledfortomorrow_post = (
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
        "[o] here's one that shouldn't be pulled up [$WEEK OF DECEMBER 16, 2012$]\n"
    )

    tasklist_tomorrowscheduled = (
        "TOMORROW:\n"
        "[ ] contact dude\n"
        "[\\] make X\n"
        "[o] call somebody [$DECEMBER 12, 2012$]\n"
        "[o] apply for something [DECEMBER 26, 2012]\n"
        "[ ] finish project\n"
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
        "[o] this task is for some day but probably not the day you're looking for [$DECEMBER 15, 2012$]\n"
        "[o] this is an old task that should have been done long ago! [$DECEMBER 3, 2012$]\n"
        "[o] this task could be the one you need to do! [$DECEMBER 10, 2012$]\n"
        "[o] this task is def not the one you need to do [$DECEMBER 19, 2012$]\n"
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

    daytemplate_undone = (
        "CHECKPOINTS:\n"
        "[x] 7:00am - wake up [9:00]\n"
        "\n"
        "AGENDA:\n"
        "[x] did do\n"
        "\t[x] this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
        "[o] i'm waitin on you! [$DECEMBER 20, 2012$]\n"
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

    periodic_month = "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
    periodic_week = "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
    periodic_day = "[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule\n"
    daythemes = "SUNDAY: Groceries Day\nMONDAY: \nTUESDAY:Cleaning Day\nWEDNESDAY:\nTHURSDAY:\nFRIDAY:\nSATURDAY: LAUNDRY DAY\n"

    def test_agenda_is_empty_when_tomorrow_and_undone_are_empty(self):
        """ Check that tomorrow's agenda is empty when no tasks are undone from today, and no tasks have been added for tomorrow """
        next_day = datetime.date(2012, 12, 10)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        tasklistfile = StringIO(self.tasklist)
        daythemesfile = StringIO(self.daythemes)
        dayfile = StringIO(self.daytemplate)
        checkpointsfile = StringIO(self.checkpoints_weekday)
        periodicfile = StringIO(self.periodic_day)
        checkpointsfile = StringIO(self.checkpoints_weekday)

        planner = PlannerMock(
            tasklistfile=tasklistfile,
            daythemesfile=daythemesfile,
            checkpoints_weekday_file=checkpointsfile,
            periodic_day_file=periodicfile,
            dayfile=dayfile,
            tomorrow_checking=config.LOGFILE_CHECKING['LAX'],
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

        templates.write_new_template(planner, Day, next_day)

        self.assertEqual(planner.dayfile.read(), daytemplate)

    def test_agenda_has_undone_tasks(self):
        """ Check that any undone tasks from today are carried over to tomorrow's agenda """
        next_day = datetime.date(2012, 12, 10)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        tasklistfile = StringIO(self.tasklist)
        daythemesfile = StringIO(self.daythemes)
        dayfile = StringIO(self.daytemplate_undone)
        checkpointsfile = StringIO(self.checkpoints_weekday)
        periodicfile = StringIO(self.periodic_day)
        checkpointsfile = StringIO(self.checkpoints_weekday)

        planner = PlannerMock(
            tasklistfile=tasklistfile,
            daythemesfile=daythemesfile,
            checkpoints_weekday_file=checkpointsfile,
            periodic_day_file=periodicfile,
            dayfile=dayfile,
            tomorrow_checking=config.LOGFILE_CHECKING['LAX'],
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
        daytemplate += "CHECKPOINTS:\n"
        daytemplate += self.checkpoints_weekday
        daytemplate += "\n"
        daytemplate += "AGENDA:\n"
        daytemplate += "[ ] s'posed to do\n"
        daytemplate += "[\\] kinda did\n"
        daytemplate += "\n"
        daytemplate += "DAILYs:\n"
        daytemplate += self.periodic_day
        daytemplate += "\n"
        daytemplate += "NOTES:\n\n\n"
        daytemplate += "TIME SPENT ON PLANNER: "

        templates.write_new_template(planner, Day, next_day)

        self.assertEqual(planner.dayfile.read(), daytemplate)

    def test_agenda_has_tomorrows_tasks(self):
        """ Check that tomorrow's agenda has tasks added for tomorrow, and that
        the tomorrow section in the tasklist is cleared once these tasks are
        added to the next day's agenda """
        next_day = datetime.date(2012, 12, 10)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        tasklistfile = StringIO(self.tasklist_tomorrow)
        daythemesfile = StringIO(self.daythemes)
        dayfile = StringIO(self.daytemplate)
        checkpointsfile = StringIO(self.checkpoints_weekday)
        periodicfile = StringIO(self.periodic_day)
        checkpointsfile = StringIO(self.checkpoints_weekday)

        planner = PlannerMock(
            tasklistfile=tasklistfile,
            daythemesfile=daythemesfile,
            checkpoints_weekday_file=checkpointsfile,
            periodic_day_file=periodicfile,
            dayfile=dayfile,
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
        daytemplate += "CHECKPOINTS:\n"
        daytemplate += self.checkpoints_weekday
        daytemplate += "\n"
        daytemplate += "AGENDA:\n"
        daytemplate += "[ ] contact dude\n"
        daytemplate += "[\\] make X\n"
        daytemplate += "[o] call somebody [$DECEMBER 12, 2012$]\n"
        daytemplate += "[o] apply for something [DECEMBER 26, 2012]\n"
        daytemplate += "[ ] finish project\n"
        daytemplate += "\n"
        daytemplate += "DAILYs:\n"
        daytemplate += self.periodic_day
        daytemplate += "\n"
        daytemplate += "NOTES:\n\n\n"
        daytemplate += "TIME SPENT ON PLANNER: "

        templates.write_new_template(planner, Day, next_day)

        self.assertEqual(planner.dayfile.read(), daytemplate)
        self.assertEqual(planner.tasklistfile.read(), self.tasklist)

    def test_agenda_has_both_tomorrows_tasks_and_undone_tasks(self):
        """ Check that tomorrow's agenda has both undone tasks from today's agenda as well as tasks added for tomorrow """
        next_day = datetime.date(2012, 12, 10)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        tasklistfile = StringIO(self.tasklist_tomorrow)
        daythemesfile = StringIO(self.daythemes)
        dayfile = StringIO(self.daytemplate_undone)
        checkpointsfile = StringIO(self.checkpoints_weekday)
        periodicfile = StringIO(self.periodic_day)
        checkpointsfile = StringIO(self.checkpoints_weekday)

        planner = PlannerMock(
            tasklistfile=tasklistfile,
            daythemesfile=daythemesfile,
            checkpoints_weekday_file=checkpointsfile,
            periodic_day_file=periodicfile,
            dayfile=dayfile,
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
        daytemplate += "CHECKPOINTS:\n"
        daytemplate += self.checkpoints_weekday
        daytemplate += "\n"
        daytemplate += "AGENDA:\n"
        daytemplate += "[ ] s'posed to do\n"
        daytemplate += "[\\] kinda did\n"
        daytemplate += "[ ] contact dude\n"
        daytemplate += "[\\] make X\n"
        daytemplate += "[o] call somebody [$DECEMBER 12, 2012$]\n"
        daytemplate += "[o] apply for something [DECEMBER 26, 2012]\n"
        daytemplate += "[ ] finish project\n"
        daytemplate += "\n"
        daytemplate += "DAILYs:\n"
        daytemplate += self.periodic_day
        daytemplate += "\n"
        daytemplate += "NOTES:\n\n\n"
        daytemplate += "TIME SPENT ON PLANNER: "

        templates.write_new_template(planner, Day, next_day)

        self.assertEqual(planner.dayfile.read(), daytemplate)

    def test_agenda_is_empty_when_scheduled_tasks_are_not_for_tomorrow(self):
        """ Check that tomorrow's agenda is empty when no scheduled tasks are scheduled for tomorrow
        (and no new tasks added for tomorrow, no tasks remaining undone from today) """
        next_day = datetime.date(2012, 12, 10)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        tasklistfile = StringIO(self.tasklist_somescheduled)
        daythemesfile = StringIO(self.daythemes)
        dayfile = StringIO(self.daytemplate)
        checkpointsfile = StringIO(self.checkpoints_weekday)
        periodicfile = StringIO(self.periodic_day)
        checkpointsfile = StringIO(self.checkpoints_weekday)

        planner = PlannerMock(
            tasklistfile=tasklistfile,
            daythemesfile=daythemesfile,
            checkpoints_weekday_file=checkpointsfile,
            periodic_day_file=periodicfile,
            dayfile=dayfile,
            tomorrow_checking=config.LOGFILE_CHECKING['LAX'],
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

        templates.write_new_template(planner, Day, next_day)

        self.assertEqual(planner.dayfile.read(), daytemplate)

    def test_agenda_contains_tasks_scheduled_for_tomorrow(self):
        """ Check that tomorrow's agenda contains scheduled tasks that are scheduled for tomorrow
        and that these tasks are removed from the scheduled section of the tasklist once processed.
        """
        next_day = datetime.date(2012, 12, 10)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        tasklistfile = StringIO(self.tasklist_scheduledfortomorrow)
        daythemesfile = StringIO(self.daythemes)
        dayfile = StringIO(self.daytemplate)
        checkpointsfile = StringIO(self.checkpoints_weekday)
        periodicfile = StringIO(self.periodic_day)
        checkpointsfile = StringIO(self.checkpoints_weekday)

        planner = PlannerMock(
            tasklistfile=tasklistfile,
            daythemesfile=daythemesfile,
            checkpoints_weekday_file=checkpointsfile,
            periodic_day_file=periodicfile,
            dayfile=dayfile,
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

        planner.tomorrow_checking = config.LOGFILE_CHECKING['LAX']
        templates.write_new_template(planner, Day, next_day)

        self.assertEqual(planner.dayfile.read(), daytemplate)
        self.assertEqual(
            planner.tasklistfile.read(),
            self.tasklist_scheduledfortomorrow_post,
        )

    def test_agenda_contains_tomorrows_undone_and_scheduled_tasks(self):
        """ Check that tomorrow's agenda contains undone tasks carried over from today, tasks added for tomorrow, as well as tasks previously scheduled for tomorrow """
        next_day = datetime.date(2012, 12, 10)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )
        tasklistfile = StringIO(self.tasklist_tomorrowscheduled)
        daythemesfile = StringIO(self.daythemes)
        dayfile = StringIO(self.daytemplate_undone)
        checkpointsfile = StringIO(self.checkpoints_weekday)
        periodicfile = StringIO(self.periodic_day)
        checkpointsfile = StringIO(self.checkpoints_weekday)

        planner = PlannerMock(
            tasklistfile=tasklistfile,
            daythemesfile=daythemesfile,
            checkpoints_weekday_file=checkpointsfile,
            periodic_day_file=periodicfile,
            dayfile=dayfile,
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
        daytemplate += "CHECKPOINTS:\n"
        daytemplate += self.checkpoints_weekday
        daytemplate += "\n"
        daytemplate += "AGENDA:\n"
        daytemplate += "[o] this is an old task that should have been done long ago! [$DECEMBER 3, 2012$]\n"
        daytemplate += "[o] this task could be the one you need to do! [$DECEMBER 10, 2012$]\n"
        daytemplate += "[ ] s'posed to do\n"
        daytemplate += "[\\] kinda did\n"
        daytemplate += "[ ] contact dude\n"
        daytemplate += "[\\] make X\n"
        daytemplate += "[o] call somebody [$DECEMBER 12, 2012$]\n"
        daytemplate += "[o] apply for something [DECEMBER 26, 2012]\n"
        daytemplate += "[ ] finish project\n"
        daytemplate += "\n"
        daytemplate += "DAILYs:\n"
        daytemplate += self.periodic_day
        daytemplate += "\n"
        daytemplate += "NOTES:\n\n\n"
        daytemplate += "TIME SPENT ON PLANNER: "

        templates.write_new_template(planner, Day, next_day)

        self.assertEqual(planner.dayfile.read(), daytemplate)
