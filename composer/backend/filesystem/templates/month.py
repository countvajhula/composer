from .base import Template


class MonthTemplate(Template):
    def load_context(self, planner, next_day):
        super(MonthTemplate, self).load_context(planner, next_day)
        self.logfile = planner.monthfile
        self.checkpointsfile = planner.monthfile
        self.checkpointsfile = planner.checkpoints_month_file
        self.periodicfile = planner.periodic_month_file

    def build(self):
        (date, month, year) = (
            self.next_day.day,
            self.next_day.strftime("%B"),
            self.next_day.year,
        )
        self.title = "= %s %d =\n" % (month.upper(), year)
        self.entry = "\t%s [[Week of %s %d, %d]]\n" % (
            self.planner.preferred_bullet_char,
            month,
            date,
            year,
        )
        self.periodicname = "MONTHLYs:\n"
        self.agenda = ""
        template = super(MonthTemplate, self).build()
        return template

    def update(self):
        (date, month, year) = (
            self.next_day.day,
            self.next_day.strftime("%B"),
            self.next_day.year,
        )
        monthcontents = self.planner.monthfile.read()
        last_week_entry = "Week of"
        previdx = monthcontents.find(last_week_entry)
        idx = monthcontents.rfind("\n", 0, previdx)
        newmonthcontents = (
            monthcontents[: idx + 1]
            + "\t%s [[Week of %s %d, %d]]\n"
            % (self.planner.preferred_bullet_char, month, date, year)
            + monthcontents[idx + 1 :]
        )
        return newmonthcontents
