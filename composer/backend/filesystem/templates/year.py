from ..utils import quarter_for_month
from .base import Template

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


class YearTemplate(Template):
    def load_context(self, planner, next_day):
        super(YearTemplate, self).load_context(planner, next_day)
        self.logfile = planner.yearfile
        self.checkpointsfile = planner.yearfile
        self.checkpointsfile = planner.checkpoints_year_file
        self.periodicfile = planner.periodic_year_file

    def build(self):
        month, year = (self.next_day.strftime("%B"), self.next_day.year)
        self.title = "= %d =\n" % year
        self.entry = "\t%s [[%s %d]]\n" % (
            self.planner.preferred_bullet_char,
            quarter_for_month(month),
            year,
        )
        self.periodicname = "YEARLYs:\n"
        self.agenda = ""
        template = super(YearTemplate, self).build()
        return template

    def update(self):
        (month, year) = (self.next_day.strftime("%B"), self.next_day.year)
        yearcontents = self.planner.yearfile.read()
        last_quarter_entry = "Q"
        previdx = yearcontents.find(last_quarter_entry)
        idx = yearcontents.rfind("\n", 0, previdx)
        newyearcontents = (
            yearcontents[: idx + 1]
            + "\t%s [[%s %d]]\n"
            % (
                self.planner.preferred_bullet_char,
                quarter_for_month(month),
                year,
            )
            + yearcontents[idx + 1 :]
        )
        return newyearcontents

    def write_existing(self):
        template = self.update()
        self.planner.yearfile = StringIO(template)

    def write_new(self):
        template = self.build()
        self.planner.yearfile = StringIO(template)
