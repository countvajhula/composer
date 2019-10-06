import re

from .base import Template
from ....timeperiod import Week


class WeekTemplate(Template):

    period = Week

    def _file_handle(self):
        return 'weekfile'

    def load_context(self, planner, for_date):
        super(WeekTemplate, self).load_context(planner, for_date)
        self.logfile = planner.weekfile
        self.checkpointsfile = planner.checkpoints_week_file
        self.periodicfile = planner.periodic_week_file
        self.theme = planner.week_theme

    def build(self, **kwargs):
        start_date = self.period.get_start_date(self.for_date)
        (date, month, year) = (
            start_date.day,
            start_date.strftime("%B"),
            start_date.year,
        )
        self.title = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
        if self.theme:
            self.title += "\n"
            self.title += "Theme: *WEEK OF %s*\n" % self.theme.upper()
        (date, month, year) = (
            self.for_date.day,
            self.for_date.strftime("%B"),
            self.for_date.year,
        )
        self.entry = "\t%s [[%s %d, %d]]\n" % (
            self.bullet_character,
            month,
            date,
            year,
        )
        self.periodicname = "WEEKLYs:\n"
        self.agenda = ""
        weektemplate = super(WeekTemplate, self).build()
        return weektemplate

    def update(self):
        """ Create a link to the new day log file in the current week log
        file.

        :returns str: The updated log file
        """
        (date, month, year) = (
            self.for_date.day,
            self.for_date.strftime("%B"),
            self.for_date.year,
        )
        weekcontents = self.logfile.read()

        entry_pattern = re.compile(
            r"\[\[([^\d ]+) (\d\d?)[, ] ?(\d{4})\]\]", re.IGNORECASE
        )
        previdx = entry_pattern.search(weekcontents).start()
        idx = weekcontents.rfind("\n", 0, previdx)
        newweekcontents = (
            weekcontents[: idx + 1]
            + "\t%s [[%s %d, %d]]\n"
            % (self.bullet_character, month, date, year)
            + weekcontents[idx + 1 :]
        )
        return newweekcontents
