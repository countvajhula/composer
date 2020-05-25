from .base import Template
from ....timeperiod import is_weekend
from ..primitives import append_files


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

    def load_context(self, planner, for_date):
        super(DayTemplate, self).load_context(planner, for_date)
        self.logfile = planner.dayfile
        if is_weekend(for_date):
            self.checkpointsfile = planner.checkpoints_weekend_file
        else:
            self.checkpointsfile = planner.checkpoints_weekday_file
        self.periodicfile = planner.periodic_day_file
        # TODO: themes could be made period-agnostic?
        self.daythemesfile = planner.daythemesfile

    def build(self, **kwargs):
        agenda = kwargs.get('with_agenda')
        (date, day, month, year) = (
            self.for_date.day,
            self.for_date.strftime("%A"),
            self.for_date.strftime("%B"),
            self.for_date.year,
        )
        self.title = (
            "= %s %s %d, %d =\n" % (day, month[:3], date, year)
        ).upper()

        theme = _get_theme_for_the_day(day, self.daythemesfile)
        if theme:
            self.title += "\n"
            self.title += "Theme: %s\n" % theme
        self.periodicname = "DAILYs:\n"

        self.agenda = agenda if agenda else ""
        # if we have successfully ensured that every entry ends in a
        # newline character, then we can safely assume here that section
        # components can be neatly concatenated
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
