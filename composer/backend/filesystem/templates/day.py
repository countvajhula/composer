from ....errors import LogfileLayoutError
from ....utils import display_message
from ..utils import (
    contain_file_mutation,
    filter_items,
    get_task_items,
    is_completed_task,
    is_invalid_task,
    is_scheduled_task,
    is_undone_task,
    is_wip_task,
    item_list_to_string,
    read_section,
)
from .base import Template


@contain_file_mutation
def _do_post_mortem(logfile):
    """ Return a list of done, undone and blocked tasks from today's agenda.
    """
    display_message(
        "Carrying over any unfinished tasks from today"
        " to tomorrow's agenda..."
    )
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


def _get_theme_for_the_day(day, daythemesfile):
    dailythemes = daythemesfile.read().lower()
    theme = dailythemes[dailythemes.index(day.lower()) :]
    theme = theme[theme.index(":") :].strip(": ")
    theme = theme[: theme.index("\n")].strip().upper()
    theme = "*" + theme + "*"
    if len(theme) > 2:
        return theme


class DayTemplate(Template):
    def _file_handle(self):
        return 'dayfile'

    def load_context(self, planner, next_day):
        super(DayTemplate, self).load_context(planner, next_day)
        self.logfile = planner.dayfile
        self.scheduled, _ = planner.get_due_tasks(next_day)
        self.tomorrow, _ = planner.get_tasks_for_tomorrow()
        self.undone = planner.get_unfinished_tasks()
        nextdow = next_day.strftime("%A")
        if nextdow.lower() in ("saturday", "sunday"):
            self.checkpointsfile = planner.checkpoints_weekend_file
        else:
            self.checkpointsfile = planner.checkpoints_weekday_file
        self.periodicfile = planner.periodic_day_file
        # TODO: themes could be made period-agnostic?
        self.daythemesfile = planner.daythemesfile

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

        theme = _get_theme_for_the_day(day, self.daythemesfile)
        if theme:
            self.title += "\n"
            self.title += "Theme: %s\n" % theme
        self.periodicname = "DAILYs:\n"

        self.agenda = ""
        # if we have successfully ensured that every task item ends in a
        # newline character, then we can safely assume here that section
        # components can be neatly concatenated
        if self.scheduled:
            self.agenda += self.scheduled
        if self.undone:
            self.agenda += self.undone
        if self.tomorrow:
            self.agenda += self.tomorrow
        daytemplate = super(DayTemplate, self).build()
        return daytemplate

    def update(self):
        # since day is the smallest period that we track, there's never a case
        # where we'd want to update an existing day file. Any information meant
        # to be in day template would already have been included at logfile
        # creation time, after which it is only manually edited to organize
        # and record details of the day
        # So updating an existing day file should be a no-op. For uniformity
        # we do return the contents of the dayfile here, so that an update
        # would be equivalent to a no-op.
        return self.logfile.read()
