from ..utils import quarter_for_month
from .base import Template

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


class QuarterTemplate(Template):

    def load_context(self, planner, next_day):
        super(QuarterTemplate, self).load_context(planner, next_day)
        self.logfile = planner.quarterfile
        self.checkpointsfile = planner.quarterfile
        self.checkpointsfile = planner.checkpoints_quarter_file
        self.periodicfile = planner.periodic_quarter_file

    def build(self):
        (month, year) = (self.next_day.strftime('%B'), self.next_day.year)
        self.title = "= %s %d =\n" % (quarter_for_month(month), year)
        self.entry = "\t%s [[Month of %s, %d]]\n" % (self.planner.preferred_bullet_char, month, year)
        self.periodicname = "QUARTERLYs:\n"
        self.agenda = ""
        template = super(QuarterTemplate, self).build()
        return template

    def update(self):
        (month, year) = (self.next_day.strftime('%B'), self.next_day.year)
        quartercontents = self.planner.quarterfile.read()
        last_month_entry = 'Month of'
        previdx = quartercontents.find(last_month_entry)
        idx = quartercontents.rfind('\n', 0, previdx)
        newquartercontents = quartercontents[:idx + 1] + '\t%s [[Month of %s, %d]]\n' % (self.planner.preferred_bullet_char, month, year) + quartercontents[idx + 1:]
        return newquartercontents

    def write_existing(self):
        template = self.update()
        self.planner.quarterfile = StringIO(template)

    def write_new(self):
        template = self.build()
        self.planner.quarterfile = StringIO(template)
