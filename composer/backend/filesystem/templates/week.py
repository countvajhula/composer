import datetime

from .base import Template


class WeekTemplate(Template):
    def _file_handle(self):
        return 'weekfile'

    def load_context(self, planner, start_date):
        super(WeekTemplate, self).load_context(planner, start_date)
        self.logfile = planner.weekfile
        self.checkpointsfile = planner.checkpoints_week_file
        self.periodicfile = planner.periodic_week_file
        self.theme = planner.week_theme

    def build(self, **kwargs):
        (date, month, year) = (
            self.start_date.day,
            self.start_date.strftime("%B"),
            self.start_date.year,
        )
        self.title = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
        if self.theme:
            self.title += "\n"
            self.title += "Theme: *WEEK OF %s*\n" % self.theme.upper()
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
            self.start_date.day,
            self.start_date.strftime("%B"),
            self.start_date.year,
        )
        weekcontents = self.logfile.read()
        previous_day = self.start_date - datetime.timedelta(days=1)
        (dateprev, monthprev, yearprev) = (
            previous_day.day,
            previous_day.strftime("%B"),
            previous_day.year,
        )
        previous_day_entry = "%s %d, %d" % (monthprev, dateprev, yearprev)
        previdx = weekcontents.find(previous_day_entry)
        idx = weekcontents.rfind("\n", 0, previdx)
        newweekcontents = (
            weekcontents[: idx + 1]
            + "\t%s [[%s %d, %d]]\n"
            % (self.bullet_character, month, date, year)
            + weekcontents[idx + 1 :]
        )
        return newweekcontents
