import datetime

from .base import Template

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


class WeekTemplate(Template):
    def load_context(self, planner, next_day):
        super(WeekTemplate, self).load_context(planner, next_day)
        self.logfile = planner.weekfile
        self.checkpointsfile = planner.weekfile
        self.checkpointsfile = planner.checkpoints_week_file
        self.periodicfile = planner.periodic_week_file

    def build(self):
        (date, month, year) = (
            self.next_day.day,
            self.next_day.strftime("%B"),
            self.next_day.year,
        )
        self.title = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
        if self.planner.week_theme:
            self.title += "\n"
            self.title += (
                "Theme: *WEEK OF %s*\n" % self.planner.week_theme.upper()
            )
        self.entry = "\t%s [[%s %d, %d]]\n" % (
            self.planner.preferred_bullet_char,
            month,
            date,
            year,
        )
        self.periodicname = "WEEKLYs:\n"
        self.agenda = ""
        weektemplate = super(WeekTemplate, self).build()
        return weektemplate

    def update(self):
        (date, month, year) = (
            self.next_day.day,
            self.next_day.strftime("%B"),
            self.next_day.year,
        )
        weekcontents = self.planner.weekfile.read()
        previous_day = self.next_day - datetime.timedelta(days=1)
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
            % (self.planner.preferred_bullet_char, month, date, year)
            + weekcontents[idx + 1 :]
        )
        return newweekcontents

    def write_existing(self):
        template = self.update()
        self.planner.weekfile = StringIO(template)

    def write_new(self):
        template = self.build()
        self.planner.weekfile = StringIO(template)
