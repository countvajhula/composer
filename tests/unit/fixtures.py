import pytest

try:  # py3
    from unittest.mock import MagicMock
except ImportError:  # py2
    from mock import MagicMock

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO

from composer.config import (
    DEFAULT_BULLET_CHARACTER,
    DEFAULT_SCHEDULE,
    LOGFILE_CHECKING,
)


class PlannerMock(MagicMock):
    """ This is needed because of the semantics of accessing and mutating
    files on the Planner, which only allows mutation via a setter, rather
    than by manually mutating the retrieved file (which will be a copy
    rather than the original). If we used a normal Mock for testing this,
    any manual mutation would reflect on the mock object whereas it wouldn't
    on an actual Planner instance, and tests may pass or fail incorrectly
    on this basis.
    """

    date = None
    tomorrow_checking = LOGFILE_CHECKING['STRICT']
    logfile_completion_checking = LOGFILE_CHECKING['STRICT']
    preferred_bullet_char = DEFAULT_BULLET_CHARACTER
    schedule = DEFAULT_SCHEDULE
    week_theme = None

    _tasklistfile = None
    _daythemesfile = None
    _dayfile = None
    _weekfile = None
    _monthfile = None
    _quarterfile = None
    _yearfile = None
    _checkpoints_weekday_file = None
    _checkpoints_weekend_file = None
    _checkpoints_week_file = None
    _checkpoints_month_file = None
    _checkpoints_quarter_file = None
    _checkpoints_year_file = None
    _periodic_day_file = None
    _periodic_week_file = None
    _periodic_month_file = None
    _periodic_quarter_file = None
    _periodic_year_file = None

    @property
    def tasklistfile(self):
        return StringIO(self._tasklistfile.getvalue())

    @tasklistfile.setter
    def tasklistfile(self, value):
        self._tasklistfile = value

    @property
    def daythemesfile(self):
        return StringIO(self._daythemesfile.getvalue())

    @daythemesfile.setter
    def daythemesfile(self, value):
        self._daythemesfile = value

    @property
    def dayfile(self):
        return StringIO(self._dayfile.getvalue())

    @dayfile.setter
    def dayfile(self, value):
        self._dayfile = value

    @property
    def weekfile(self):
        return StringIO(self._weekfile.getvalue())

    @weekfile.setter
    def weekfile(self, value):
        self._weekfile = value

    @property
    def monthfile(self):
        return StringIO(self._monthfile.getvalue())

    @monthfile.setter
    def monthfile(self, value):
        self._monthfile = value

    @property
    def quarterfile(self):
        return StringIO(self._quarterfile.getvalue())

    @quarterfile.setter
    def quarterfile(self, value):
        self._quarterfile = value

    @property
    def yearfile(self):
        return StringIO(self._yearfile.getvalue())

    @yearfile.setter
    def yearfile(self, value):
        self._yearfile = value


def _logfile():
    contents = (
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
    )
    return StringIO(contents)


def _empty_logfile():
    return StringIO("")


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
def logfile():
    return _logfile()


@pytest.fixture
def empty_logfile():
    return _empty_logfile()


@pytest.fixture
def tasklist_file():
    return _tasklistfile()


@pytest.fixture
def planner():
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

    planner = PlannerMock(
        tasklistfile=StringIO(tasklist),
        daythemesfile=StringIO(daythemes),
        periodic_day_file=StringIO(periodic_day),
        periodic_week_file=StringIO(periodic_week),
        periodic_month_file=StringIO(periodic_month),
        checkpoints_weekday_file=StringIO(checkpoints_weekday),
        checkpoints_weekend_file=StringIO(checkpoints_weekend),
        checkpoints_week_file=StringIO(checkpoints_week),
        checkpoints_month_file=StringIO(checkpoints_month),
        dayfile=StringIO(daytemplate),
        weekfile=StringIO(weektemplate),
        monthfile=StringIO(monthtemplate),
    )
    return planner
