import datetime
import pytest

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO

from composer.backend import FilesystemPlanner
from composer.backend.base import PlannerBase
from composer.timeperiod import Year


def _config_file():
    contents = (
        "[general]\n"
        "wikis=/Users/siddhartha/log/themanwiki,/Users/siddhartha/log/ferdywiki,/Users/siddhartha/log/planner\n"
        "lessons_files=Lessons_Introspective.wiki,Lessons_General.wiki,Lessons_Advice.wiki,Lessons_Experimental.wiki\n"
        "; schedule is the daily schedule to use -- if you set a value of 'abc'\n"
        "; then there should be files called Checkpoints_Weekday_Abc.wiki\n"
        "; and Checkpoints_Weekend_Abc.wiki at the wiki path\n"
        "; e.g. /Users/myuser/log/wiki/Checkpoints_Weekday_Abc.wiki\n"
        "schedule=standard\n"
        "bullet_character=*\n"
    )
    return StringIO(contents)


@pytest.fixture
def config_file():
    return _config_file()


def _wiki_config_file():
    contents = "[general]\n" "bullet_character=-\n"
    return StringIO(contents)


@pytest.fixture
def wiki_config_file():
    return _wiki_config_file()


def _logfile():
    contents = (
        "AGENDA:\n"
        "[ ] a task\n"
        "[\\] a WIP task\n"
        "Just some additional clarifications\n"
        "\n"
        "[o] a scheduled task [$TOMORROW$]\n"
        "[ ] a task with subtasks\n"
        "\t[ ] first thing\n"
        "\tclarification of first thing\n"
        "\t[ ] second thing\n"
        "[ ] another task\n"
        "\n"
        "NOTES:\n"
    )
    return StringIO(contents)


@pytest.fixture
def logfile():
    return _logfile()


def _empty_logfile():
    return StringIO("")


@pytest.fixture
def empty_logfile():
    return _empty_logfile()


def _complete_logfile():
    return StringIO(_logfile().read() + "Did lots of things today.\n")


@pytest.fixture
def complete_logfile():
    return _complete_logfile()


def _tasklistfile():
    contents = (
        "TOMORROW:\n"
        "[ ] a task\n"
        "[\\] a WIP task\n"
        "Just some additional clarifications\n"
        "\n"
        "[o] a scheduled task [$TOMORROW$]\n"
        "THIS WEEK:\n"
        "[ ] a task with subtasks\n"
        "\t[\\] first thing\n"
        "\tclarification of first thing\n"
        "\t[ ] second thing\n"
        "THIS MONTH:\n"
        "UNSCHEDULED:\n"
        "[ ] another task\n"
    )
    return StringIO(contents)


@pytest.fixture
def tasklist_file():
    return _tasklistfile()


def _planner_base():
    class DummyPlanner(PlannerBase):
        def construct(self, location=None):
            pass

        def get_agenda(self, period):
            pass

        def update_agenda(self, period, agenda):
            pass

        def check_log_completion(self, period):
            pass

        def schedule_tasks(self):
            pass

        def get_due_tasks(self, for_day):
            pass

        def get_tasks_for_tomorrow(self):
            pass

        def get_todays_unfinished_tasks(self):
            pass

        def create_log(self, period, next_day):
            pass

        def update_log(self, period, next_day):
            pass

        def is_ok_to_advance(self, period=Year):
            pass

        def save(self, period=None):
            pass

    planner = DummyPlanner()
    planner.date = datetime.date.today()
    planner.location = ''
    return planner


@pytest.fixture
def planner_base():
    return _planner_base()


def _planner():
    tasklist = (
        "TOMORROW:\n"
        "[ ] contact dude\n"
        "[\\] make X\n"
        "[ ] call somebody\n"
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

    yeartemplate = (
        "= 2012 =\n"
        "\n"
        'Theme: *"PUT IT BACK" 2012*\n'
        "\n"
        "\t* [[Q4 2015]]\n"
        "\t* [[Q3 2015]]\n"
        "\t* [[Q2 2015]]\n"
        "\t* [[Q1 2015]]\n"
        "\n"
        "CHECKPOINTS:\n"
        "[ ] Q1 - []\n"
        "[ ] Q2 - []\n"
        "[ ] Q3 - []\n"
        "[ ] Q4 - []\n"
        "\n"
        "AGENDA:\n"
        "\n"
        "YEARLYs:\n"
        "[ ] 1 significant life achievement\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: \n"
    )

    quartertemplate = (
        "= Q4 2012 =\n"
        "\n"
        "\t* [[Month of December, 2012]]\n"
        "\t* [[Month of November, 2012]]\n"
        "\t* [[Month of October, 2012]]\n"
        "\n"
        "CHECKPOINTS:\n"
        "[ ] MONTH 1 - []\n"
        "[ ] MONTH 2 - []\n"
        "[ ] MONTH 3 - []\n"
        "\n"
        "AGENDA:\n"
        "\n"
        "QUARTERLYs:\n"
        "[ ] 1 major research achievement\n"
        "[ ] 1 major coding achievement\n"
        "[ ] 1 unique achievement\n"
        "[ ] update financials\n"
        "\n"
        "NOTES:\n"
        "\n"
        "\n"
        "TIME SPENT ON PLANNER: \n"
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
        "[x] did do\n"
        "\t[x] this\n"
        "\t[x] and this\n"
        "[ ] s'posed to do\n"
        "[\\] kinda did\n"
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
    daythemes = (
        "SUNDAY: Groceries Day\n"
        "MONDAY: \n"
        "TUESDAY:Cleaning Day\n"
        "WEDNESDAY:\n"
        "THURSDAY:\n"
        "FRIDAY:\n"
        "SATURDAY: LAUNDRY DAY\n"
    )

    planner = FilesystemPlanner()
    planner.tasklistfile = StringIO(tasklist)
    planner.daythemesfile = StringIO(daythemes)
    planner.periodic_day_file = StringIO(periodic_day)
    planner.periodic_week_file = StringIO(periodic_week)
    planner.periodic_month_file = StringIO(periodic_month)
    planner.checkpoints_weekday_file = StringIO(checkpoints_weekday)
    planner.checkpoints_weekend_file = StringIO(checkpoints_weekend)
    planner.checkpoints_week_file = StringIO(checkpoints_week)
    planner.checkpoints_month_file = StringIO(checkpoints_month)
    planner.dayfile = StringIO(daytemplate)
    planner.weekfile = StringIO(weektemplate)
    planner.monthfile = StringIO(monthtemplate)
    planner.quarterfile = StringIO(quartertemplate)
    planner.yearfile = StringIO(yeartemplate)
    planner.next_day_planner = FilesystemPlanner()

    planner.date = datetime.date.today()
    planner.location = ''

    return planner


@pytest.fixture
def planner():
    return _planner()
