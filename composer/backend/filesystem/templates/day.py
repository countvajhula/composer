from .... import config
from ....errors import (
    LogfileLayoutError,
    TasklistLayoutError,
    TomorrowIsEmptyError,
)
from .. import scheduling
from ..utils import (
    SECTION_HEADER_PATTERN,
    TASK_PATTERN,
    is_completed_task,
    is_invalid_task,
    is_scheduled_task,
    is_task,
    is_undone_task,
    is_wip_task,
)
from .base import Template

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


def _do_post_mortem(logfile):
    tasks = {"done": "", "undone": "", "blocked": ""}
    ss = logfile.readline()
    while ss != "" and ss[: len("agenda")].lower() != "agenda":
        ss = logfile.readline()
    if ss == "":
        raise LogfileLayoutError(
            "No AGENDA section found in today's log file!"
            " Add one and try again."
        )
    ss = logfile.readline()
    while ss != "" and not SECTION_HEADER_PATTERN.search(ss):
        if is_completed_task(ss) or is_invalid_task(ss):
            tasks["done"] += ss
            ss = logfile.readline()
            while (
                ss != ""
                and not is_task(ss)
                and not SECTION_HEADER_PATTERN.search(ss)
            ):
                tasks["done"] += ss
                ss = logfile.readline()
        elif is_undone_task(ss) or is_wip_task(ss):
            tasks["undone"] += ss
            ss = logfile.readline()
            while (
                ss != ""
                and not is_task(ss)
                and not SECTION_HEADER_PATTERN.search(ss)
            ):
                tasks["undone"] += ss
                ss = logfile.readline()
        elif is_scheduled_task(ss):
            tasks["blocked"] += ss
            ss = logfile.readline()
            while (
                ss != ""
                and not is_task(ss)
                and not SECTION_HEADER_PATTERN.search(ss)
            ):
                tasks["blocked"] += ss
                ss = logfile.readline()
        else:
            ss = logfile.readline()
    tasks["done"] = tasks["done"].strip("\n")
    tasks["undone"] = tasks["undone"].strip("\n")
    tasks["blocked"] = tasks["blocked"].strip("\n")
    return tasks


def _get_tasks_for_tomorrow(tasklist, tomorrow_checking):
    """ Read the tasklist, parse all tasks under the TOMORROW section
    and return those, and also return a modified tasklist with those
    tasks removed """
    tasks = ""
    tasklist_nextday = StringIO()
    ss = tasklist.readline()
    while ss != "" and ss[: len("tomorrow")].lower() != "tomorrow":
        tasklist_nextday.write(ss)
        ss = tasklist.readline()
    if ss == "":
        raise TasklistLayoutError(
            "Error: No 'TOMORROW' section found in your tasklist!"
            " Please add one and try again."
        )
    tasklist_nextday.write(ss)
    ss = tasklist.readline()
    while ss != "" and not SECTION_HEADER_PATTERN.search(ss):
        if TASK_PATTERN.search(ss):
            tasks += ss
        else:
            tasklist_nextday.write(ss)
        ss = tasklist.readline()
    if tasks == "" and tomorrow_checking == config.LOGFILE_CHECKING["STRICT"]:
        raise TomorrowIsEmptyError(
            "The tomorrow section is blank. Do you want to add"
            " some tasks for tomorrow?"
        )
    while ss != "":
        tasklist_nextday.write(ss)
        ss = tasklist.readline()
    tasks = tasks.strip("\n")
    tasklist_nextday.seek(0)
    return tasks, tasklist_nextday


def _get_theme_for_the_day(day, daythemesfile):
    dailythemes = daythemesfile.read().lower()
    theme = dailythemes[dailythemes.index(day.lower()) :]
    theme = theme[theme.index(":") :].strip(": ")
    theme = theme[: theme.index("\n")].strip().upper()
    theme = "*" + theme + "*"
    if len(theme) > 2:
        return theme


class DayTemplate(Template):
    def load_context(self, planner, next_day):
        super(DayTemplate, self).load_context(planner, next_day)
        self.logfile = planner.dayfile
        self.checkpointsfile = planner.dayfile
        nextdow = next_day.strftime("%A")
        if nextdow.lower() in ("saturday", "sunday"):
            self.checkpointsfile = planner.checkpoints_weekend_file
        else:
            self.checkpointsfile = planner.checkpoints_weekday_file
        self.periodicfile = planner.periodic_day_file

    def build(self):
        (date, day, month, year) = (
            self.next_day.day,
            self.next_day.strftime("%A"),
            self.next_day.strftime("%B"),
            self.next_day.year,
        )
        self.title = (
            "= %s %s %d, %d =\n" % (day, month[:3], date, year)
        ).upper()

        theme = _get_theme_for_the_day(day, self.planner.daythemesfile)
        if theme:
            self.title += "\n"
            self.title += "Theme: %s\n" % theme
        self.periodicname = "DAILYs:\n"
        undone = _do_post_mortem(self.planner.dayfile)["undone"]
        tasklistfile = self.tasklistfile  # initial state of tasklist file
        scheduled, tasklistfile = scheduling.get_scheduled_tasks(
            tasklistfile, self.next_day
        )
        tomorrow, tasklistfile = _get_tasks_for_tomorrow(
            tasklistfile, self.planner.tomorrow_checking
        )
        # TODO: do this mutation elsewhere
        self.planner.tasklistfile = (
            tasklistfile
        )  # update the tasklist file to the post-processed version
        self.agenda = ""
        if scheduled:
            self.agenda += scheduled
        if undone:
            if self.agenda:
                self.agenda += "\n" + undone
            else:
                self.agenda += undone
        if tomorrow:
            if self.agenda:
                self.agenda += "\n" + tomorrow
            else:
                self.agenda += tomorrow
        daytemplate = super(DayTemplate, self).build()
        return daytemplate

    def update(self):
        pass

    def write_existing(self):
        # if period is DAY, noop
        pass

    def write_new(self):
        template = self.build()
        self.planner.dayfile = StringIO(template)
