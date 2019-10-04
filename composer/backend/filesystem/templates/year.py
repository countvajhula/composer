from ..primitives import quarter_for_month
from .base import Template


class YearTemplate(Template):

    def _file_handle(self):
        return 'yearfile'

    def load_context(self, planner, start_date):
        super(YearTemplate, self).load_context(planner, start_date)
        self.logfile = planner.yearfile
        self.checkpointsfile = planner.checkpoints_year_file
        self.periodicfile = planner.periodic_year_file

    def build(self, **kwargs):
        month, year = (self.start_date.strftime("%B"), self.start_date.year)
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
        """ Create a link to the new quarter log file in the current year log
        file.

        :returns str: The updated log file
        """
        (month, year) = (self.start_date.strftime("%B"), self.start_date.year)
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
