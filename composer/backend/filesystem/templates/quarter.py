from ....timeperiod import quarter_for_month
from .base import Template


class QuarterTemplate(Template):
    def _file_handle(self):
        return 'quarterfile'

    def load_context(self, planner, for_date):
        super(QuarterTemplate, self).load_context(planner, for_date)
        self.logfile = planner.quarterfile
        self.checkpointsfile = planner.checkpoints_quarter_file
        self.periodicfile = planner.periodic_quarter_file

    def build(self, **kwargs):
        self.title = "= %s %d =\n" % (
            quarter_for_month(self.for_date.month),
            self.for_date.year,
        )
        month_name = self.for_date.strftime("%B")
        self.entry = "\t%s [[Month of %s, %d]]\n" % (
            self.bullet_character,
            month_name,
            self.for_date.year,
        )
        self.periodicname = "QUARTERLYs:\n"
        self.agenda = ""
        template = super(QuarterTemplate, self).build()
        return template

    def update(self):
        """ Create a link to the new month log file in the current quarter log
        file.

        :returns str: The updated log file
        """
        quartercontents = self.logfile.read()
        last_month_entry = "Month of"
        previdx = quartercontents.find(last_month_entry)
        idx = quartercontents.rfind("\n", 0, previdx)
        month_name = self.for_date.strftime("%B")
        newquartercontents = (
            quartercontents[: idx + 1]
            + "\t%s [[Month of %s, %d]]\n"
            % (self.bullet_character, month_name, self.for_date.year)
            + quartercontents[idx + 1 :]
        )
        return newquartercontents
