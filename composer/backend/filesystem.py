import os

from datetime import datetime

from .base import PlannerBase
from .. import config
from ..utils import write_file

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


SCHEDULE_FILE_PREFIX = 'Checkpoints'
PLANNERTASKLISTFILE = 'TaskList.wiki'
PLANNERDAYTHEMESFILELINK = 'DayThemes.wiki'
PLANNERDAYFILELINK = 'currentday'
PLANNERWEEKFILELINK = 'currentweek'
PLANNERMONTHFILELINK = 'currentmonth'
PLANNERQUARTERFILELINK = 'currentquarter'
PLANNERYEARFILELINK = 'currentyear'
CHECKPOINTSWEEKFILE = 'Checkpoints_Week.wiki'
CHECKPOINTSMONTHFILE = 'Checkpoints_Month.wiki'
CHECKPOINTSQUARTERFILE = 'Checkpoints_Quarter.wiki'
CHECKPOINTSYEARFILE = 'Checkpoints_Year.wiki'
PERIODICYEARLYFILE = 'Periodic_Yearly.wiki'
PERIODICQUARTERLYFILE = 'Periodic_Quarterly.wiki'
PERIODICMONTHLYFILE = 'Periodic_Monthly.wiki'
PERIODICWEEKLYFILE = 'Periodic_Weekly.wiki'
PERIODICDAILYFILE = 'Periodic_Daily.wiki'


class FilesystemPlanner(PlannerBase):
    tasklistfile = None
    daythemesfile = None
    dayfile = None
    weekfile = None
    monthfile = None
    quarterfile = None
    yearfile = None
    checkpoints_weekday_file = None
    checkpoints_weekend_file = None
    checkpoints_week_file = None
    checkpoints_month_file = None
    checkpoints_quarter_file = None
    checkpoints_year_file = None
    periodic_day_file = None
    periodic_week_file = None
    periodic_month_file = None
    periodic_quarter_file = None
    periodic_year_file = None

    def __init__(self, location=None):
        self.construct(location)

    def _read_file(self, filename):
        """ Read a file on disk and produce an in-memory logical representation
        of the file. This logical representation will be used for analysis and
        processing so that the actual file on disk isn't affected until any
        such processing is complete.
        """
        with open(filename, 'r') as f:
            result = StringIO(f.read())
        return result

    def _get_date(self):
        """ get planner date, currently looks for the file 'currentday', if dne throw exception """
        plannerdatelink = '%s/%s' % (self.location, PLANNERDAYFILELINK)
        plannerdatefn = os.readlink(plannerdatelink)
        pathidx = plannerdatefn.rfind('/')
        datestr = plannerdatefn[pathidx + 1:-5]  # trim path from beginning and '.wiki' from end
        plannerdate = datetime.strptime(datestr, '%B %d, %Y').date()
        return plannerdate

    def construct(self, location=None):
        """ Construct a planner object from a filesystem representation."""
        # CURRENT planner date used here
        if location is None:
            # needed for tests atm -- eventually make location a required arg
            return
        self.location = location
        self.date = self._get_date()
        self.tasklistfile = self._read_file('{}/{}'.format(location, PLANNERTASKLISTFILE))
        self.daythemesfile = self._read_file('{}/{}'.format(location, PLANNERDAYTHEMESFILELINK))
        self.dayfile = self._read_file('{}/{}'.format(location, PLANNERDAYFILELINK))
        self.weekfile = self._read_file('{}/{}'.format(location, PLANNERWEEKFILELINK))
        self.monthfile = self._read_file('{}/{}'.format(location, PLANNERMONTHFILELINK))
        self.quarterfile = self._read_file('{}/{}'.format(location, PLANNERQUARTERFILELINK))
        self.yearfile = self._read_file('{}/{}'.format(location, PLANNERYEARFILELINK))

        # daily, weekly, monthly checkpoints, periodic items
        self.checkpoints_weekday_file = self._read_file(
            '{}/{}_Weekday_{}.wiki'
            .format(location,
                    SCHEDULE_FILE_PREFIX,
                    config.PlannerConfig.Schedule.capitalize()))
        self.checkpoints_weekend_file = self._read_file(
            '{}/{}_Weekend_{}.wiki'
            .format(location,
                    SCHEDULE_FILE_PREFIX,
                    config.PlannerConfig.Schedule.capitalize()))
        self.periodic_day_file = self._read_file('{}/{}'.format(location, PERIODICDAILYFILE))
        self.checkpoints_week_file = self._read_file('{}/{}'.format(location, CHECKPOINTSWEEKFILE))
        self.periodic_week_file = self._read_file('{}/{}'.format(location, PERIODICWEEKLYFILE))
        self.checkpoints_month_file = self._read_file('{}/{}'.format(location, CHECKPOINTSMONTHFILE))
        self.periodic_month_file = self._read_file('{}/{}'.format(location, PERIODICMONTHLYFILE))
        self.checkpoints_quarter_file = self._read_file('{}/{}'.format(location, CHECKPOINTSQUARTERFILE))
        self.periodic_quarter_file = self._read_file('{}/{}'.format(location, PERIODICQUARTERLYFILE))
        self.checkpoints_year_file = self._read_file('{}/{}'.format(location, CHECKPOINTSYEARFILE))
        self.periodic_year_file = self._read_file('{}/{}'.format(location, PERIODICYEARLYFILE))

    def reset_heads_on_files(self):
        # TODO: define relevant atomic operations so that this isn't necessary
        self.tasklistfile.seek(0)
        self.daythemesfile.seek(0)
        self.dayfile.seek(0)
        self.weekfile.seek(0)
        self.monthfile.seek(0)
        self.quarterfile.seek(0)
        self.yearfile.seek(0)
        self.checkpoints_year_file.seek(0)
        self.periodic_year_file.seek(0)
        self.checkpoints_quarter_file.seek(0)
        self.periodic_quarter_file.seek(0)
        self.checkpoints_month_file.seek(0)
        self.periodic_month_file.seek(0)
        self.checkpoints_week_file.seek(0)
        self.periodic_week_file.seek(0)
        self.checkpoints_weekday_file.seek(0)
        self.checkpoints_weekend_file.seek(0)
        self.periodic_day_file.seek(0)

    def save(self):
        """ Write the planner object to the filesystem at the given path."""
        pathspec = '{}/{}'
        tasklist_filename = pathspec.format(self.location, PLANNERTASKLISTFILE)
        day_filename = os.path.realpath(pathspec.format(self.location, PLANNERDAYFILELINK))
        week_filename = os.path.realpath(pathspec.format(self.location, PLANNERWEEKFILELINK))
        month_filename = os.path.realpath(pathspec.format(self.location, PLANNERMONTHFILELINK))
        quarter_filename = os.path.realpath(pathspec.format(self.location, PLANNERQUARTERFILELINK))
        year_filename = os.path.realpath(pathspec.format(self.location, PLANNERYEARFILELINK))

        write_file(self.tasklistfile.read(), tasklist_filename)
        write_file(self.yearfile.read(), year_filename)
        write_file(self.quarterfile.read(), quarter_filename)
        write_file(self.monthfile.read(), month_filename)
        write_file(self.weekfile.read(), week_filename)
        write_file(self.dayfile.read(), day_filename)

        self.reset_heads_on_files()
