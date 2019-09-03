from ..utils import quarter_for_month
from .base import Template


class YearTemplate(Template):
    def _file_handle(self):
        return 'yearfile'

    def load_context(self, planner, next_day):
        super(YearTemplate, self).load_context(planner, next_day)
        self.logfile = planner.yearfile
        self.checkpointsfile = planner.checkpoints_year_file
        self.periodicfile = planner.periodic_year_file

    def build(self):
        month, year = (self.next_day.strftime("%B"), self.next_day.year)
        self.title = "= %d =\n" % year
        self.entry = "\t%s [[%s %d]]\n" % (
            self.bullet_character,
            quarter_for_month(month),
            year,
        )
        self.periodicname = "YEARLYs:\n"
        self.agenda = ""
        template = super(YearTemplate, self).build()
        return template

    def update(self):
        (month, year) = (self.next_day.strftime("%B"), self.next_day.year)
        yearcontents = self.logfile.read()
        last_quarter_entry = "Q"
        previdx = yearcontents.find(last_quarter_entry)
        idx = yearcontents.rfind("\n", 0, previdx)
        newyearcontents = (
            yearcontents[: idx + 1]
            + "\t%s [[%s %d]]\n"
            % (self.bullet_character, quarter_for_month(month), year)
            + yearcontents[idx + 1 :]
        )
        return newyearcontents
