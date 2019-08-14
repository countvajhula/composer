import datetime
import unittest

import composer.backend.filesystem.scheduling as scheduling
from composer.backend import FilesystemPlanner

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


class PlannerTaskSchedulingTester(unittest.TestCase):
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

    tasklist_scheduledbadformat = (
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
        "[ ] remember to do this\n"
    )

    tasklist_somescheduled = (
        "TOMORROW:\n"
        "[ ] contact dude\n"
        "[\\] make X\n"
        "[o] call somebody [$DECEMBER 12, 2012$]\n"
        "[o] apply for something [DECEMBER 26, 2012]\n"
        "[ ] finish project\n"
        "\n"
        "THIS WEEK:\n"
        "[\\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
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
        "SCHEDULED:\n"
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
        "[o] still waitin on you [$JANUARY 14, 2013$]\n"
    )

    tasklist_tasklist = (
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
        "[o] some misplaced scheduled task [$DECEMBER 14, 2012$]\n"
        "[o] another scheduled task that's lost its way [$DECEMBER 19, 2012$]\n"
    )

    tasklist_tasklist_agenda = (
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
        "[o] some misplaced scheduled task [$DECEMBER 14, 2012$]\n"
        "[o] another scheduled task that's lost its way [$DECEMBER 19, 2012$]\n"
        "[o] i'm waitin on you! [$DECEMBER 20, 2012$]\n"
        "[o] still waitin on you [$JANUARY 14, 2013$]\n"
    )

    tasklist_scheduled_formats1to4and11to13 = (
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
        "[o] i'm waitin on you! [$DECEMBER 20, 2012$]\n"
        "[o] still waitin on you [$JANUARY 14, 2013$]\n"
    )

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
        "\n"
        "UNSCHEDULED:\n"
        "\n"
        "SCHEDULED:\n"
        "[o] i'm waitin on you! [$WEEK OF DECEMBER 16, 2012$]\n"
        "[o] still waitin on you [$WEEK OF JANUARY 13, 2013$]\n"
    )

    tasklist_scheduled_formats9to10and15 = (
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
        "[o] i'm waitin on you! [$DECEMBER 2012$]\n"
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
        "[o] i'm waitin till sunday! [$DECEMBER 9, 2012$]\n"
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

    def test_agenda_scheduled_tasks_are_scheduled(self):
        """ Check that scheduling tasks pulls all scheduled tasks from today's Agenda
        into the SCHEDULED section of the tasklist """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(), self.tasklist_agenda
        )

    def test_task_list_scheduled_tasks_are_scheduled(self):
        """ Check that scheduling tasks pulls all scheduled tasks from the TaskList
        into the SCHEDULED section of the tasklist """
        self.planner.tasklistfile = StringIO(self.tasklist_somescheduled)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(), self.tasklist_tasklist
        )

    def test_both_agenda_and_task_list_scheduled_tasks_are_scheduled(self):
        """ Check that scheduling tasks pulls all scheduled tasks from the TaskList and
        today's agenda into the SCHEDULED section of the tasklist """
        self.planner.tasklistfile = StringIO(self.tasklist_somescheduled)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(), self.tasklist_tasklist_agenda
        )

    def test_scheduled_task_without_date_raises_exception(self):
        """ Check that is a task is marked as scheduled but no date is provided, that
        an exception is thrown """
        self.planner.dayfile = StringIO(self.daytemplate_noscheduledate)
        self.assertRaises(Exception, scheduling.schedule_tasks, self.planner)

    def test_badly_formatted_scheduled_task_raises_exception(self):
        """ Check that a task already present in the SCHEDULED section and formatted incorrectly raises an Exception """
        self.planner.tasklistfile = StringIO(self.tasklist_scheduledbadformat)
        self.assertRaises(Exception, scheduling.schedule_tasks, self.planner)

    def test_schedule_date_format1(self):
        """ Check that the format MONTH DD, YYYY works (w optional space or comma or both) """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format1)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format2(self):
        """ Check that the format DD MONTH, YYYY works (w optional space or comma or both) """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format2)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format3(self):
        """ Check that the format MONTH DD works """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format3)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format4(self):
        """ Check that the format DD MONTH works """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format4)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format5(self):
        """ Check that the format WEEK OF MONTH DD, YYYY works (w optional space or comma or both) """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format5)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats5to8and14,
        )

    def test_schedule_date_format6(self):
        """ Check that the format WEEK OF DD MONTH, YYYY works (w optional space or comma or both) """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format6)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats5to8and14,
        )

    def test_schedule_date_format7(self):
        """ Check that the format WEEK OF MONTH DD works """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format7)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats5to8and14,
        )

    def test_schedule_date_format8(self):
        """ Check that the format WEEK OF DD MONTH works """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format8)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats5to8and14,
        )

    def test_schedule_date_format9(self):
        """ Check that the format MONTH YYYY works (w optional space or comma or both) """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format9)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats9to10and15,
        )

    def test_schedule_date_format10(self):
        """ Check that the format MONTH works """
        self.planner.date = datetime.date(2012, 11, 4)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format10)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats9to10and15,
        )

    def test_schedule_date_format11(self):
        """ Check that the format MM/DD/YYYY works """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format11)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format12(self):
        """ Check that the format MM-DD-YYYY works """
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format12)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format13(self):
        """ Check that the format TOMORROW works """
        self.planner.date = datetime.date(2012, 12, 19)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format13)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats1to4and11to13,
        )

    def test_schedule_date_format14(self):
        """ Check that the format NEXT WEEK works """
        self.planner.date = datetime.date(2012, 12, 10)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format14)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats5to8and14,
        )

    def test_schedule_date_format15(self):
        """ Check that the format NEXT MONTH works """
        self.planner.date = datetime.date(2012, 12, 3)
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format15)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats9to10and15,
        )

    def test_schedule_date_format16(self):
        """ Check that the format <DOW> works """
        self.planner.date = datetime.date(2012, 12, 3)  # monday
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format16)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats16and17,
        )

    def test_schedule_date_format17(self):
        """ Check that the format <DOW> (abbrv.) works """
        self.planner.date = datetime.date(2012, 12, 3)  # monday
        self.planner.dayfile = StringIO(self.daytemplate_scheduled_format17)
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats16and17,
        )

    def test_schedule_date_is_case_insensitive(self):
        """ Check that schedule date is case insensitive, by testing a lowercase month """
        self.planner.date = datetime.date(2012, 11, 4)
        self.planner.dayfile = StringIO(
            self.daytemplate_scheduled_format10_lowercase
        )
        scheduling.schedule_tasks(self.planner)
        self.assertEqual(
            self.planner.tasklistfile.read(),
            self.tasklist_scheduled_formats9to10and15,
        )
