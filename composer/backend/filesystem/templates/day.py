from .... import config
from ....errors import (
    LogfileLayoutError,
    TasklistLayoutError,
    TomorrowIsEmptyError,
)
from .. import scheduling
from ..utils import (
    SECTION_PATTERN,
    TASK_PATTERN,
    filter_items,
    get_task_items,
    is_completed_task,
    is_invalid_task,
    is_scheduled_task,
    is_task,
    is_undone_task,
    is_wip_task,
    item_list_to_string,
    read_section,
)
from .base import Template

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


def _do_post_mortem(logfile):
    """ Return a list of done, undone and blocked tasks from today's agenda.
    """
    try:
        tasks, _ = read_section(logfile, 'agenda')
    except ValueError:
        raise LogfileLayoutError(
            "No AGENDA section found in today's log file!"
            " Add one and try again."
        )
    items = get_task_items(tasks)
    done = filter_items(
        items, lambda item: (is_completed_task(item) or is_invalid_task(item))
    )
    undone = filter_items(
        items, lambda item: (is_undone_task(item) or is_wip_task(item))
    )
    blocked = filter_items(items, is_scheduled_task)
    done, undone, blocked = map(item_list_to_string, (done, undone, blocked))

    return done, undone, blocked


def _get_tasks_for_tomorrow(tasklist, tomorrow_checking):
    """ Read the tasklist, parse all tasks under the TOMORROW section
    and return those, and also return a modified tasklist with those
    tasks removed """
    try:
        tasks, tasklist_nextday = read_section(tasklist, 'tomorrow')
    except ValueError:
        raise TasklistLayoutError(
            "Error: No 'TOMORROW' section found in your tasklist!"
            " Please add one and try again."
        )
    if (
        tasks.getvalue() == ""
        and tomorrow_checking == config.LOGFILE_CHECKING["STRICT"]
    ):
        raise TomorrowIsEmptyError(
            "The tomorrow section is blank. Do you want to add"
            " some tasks for tomorrow?"
        )
    return tasks.read(), tasklist_nextday


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
        _, undone, _ = _do_post_mortem(self.planner.dayfile)
        tasklistfile = self.tasklistfile  # initial state of tasklist file
        scheduled, tasklistfile = scheduling.get_due_tasks(
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
        # with every task item ending in a newline character, we will
        # assume that section components can be neatly concatenated
        if scheduled:
            self.agenda += scheduled
        if undone:
            self.agenda += undone
        if tomorrow:
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
