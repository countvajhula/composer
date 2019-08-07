import datetime

from . import config
from . import scheduling
from . import utils
from .errors import (
    LogfileLayoutError,
    TasklistLayoutError,
    TomorrowIsEmptyError)
from .utils import SECTION_HEADER_PATTERN, TASK_PATTERN

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


def do_post_mortem(logfile):
    tasks = {'done': '', 'undone': '', 'blocked': ''}
    ss = logfile.readline()
    while ss != '' and ss[:len('agenda')].lower() != 'agenda':
        ss = logfile.readline()
    if ss == '':
        raise LogfileLayoutError("No AGENDA section found in today's log file! Add one and try again.")
    ss = logfile.readline()
    while ss != '' and not SECTION_HEADER_PATTERN.search(ss):
        if ss.startswith('[x') or ss.startswith('[-'):
            tasks['done'] += ss
            ss = logfile.readline()
            while ss != '' and not ss.startswith('[') and not SECTION_HEADER_PATTERN.search(ss):
                tasks['done'] += ss
                ss = logfile.readline()
        elif ss.startswith('[ ') or ss.startswith('[\\'):
            tasks['undone'] += ss
            ss = logfile.readline()
            while ss != '' and not ss.startswith('[') and not SECTION_HEADER_PATTERN.search(ss):
                tasks['undone'] += ss
                ss = logfile.readline()
        elif ss.startswith('[o'):
            tasks['blocked'] += ss
            ss = logfile.readline()
            while ss != '' and not ss.startswith('[') and not SECTION_HEADER_PATTERN.search(ss):
                tasks['blocked'] += ss
                ss = logfile.readline()
        else:
            ss = logfile.readline()
    logfile.seek(0)
    tasks['done'] = tasks['done'].strip('\n')
    tasks['undone'] = tasks['undone'].strip('\n')
    tasks['blocked'] = tasks['blocked'].strip('\n')
    return tasks


def get_tasks_for_tomorrow(tasklist):
    """ Read the tasklist, parse all tasks under the TOMORROW section and return those,
    and remove them from the tasklist """
    tasks = ''
    tasklist_nextday = StringIO()
    ss = tasklist.readline()
    while ss != '' and ss[:len('tomorrow')].lower() != 'tomorrow':
        tasklist_nextday.write(ss)
        ss = tasklist.readline()
    if ss == '':
        raise TasklistLayoutError("Error: No 'TOMORROW' section found in your tasklist! Please add one and try again.")
    tasklist_nextday.write(ss)
    ss = tasklist.readline()
    while ss != '' and not SECTION_HEADER_PATTERN.search(ss):
        if TASK_PATTERN.search(ss):
            tasks += ss
        else:
            tasklist_nextday.write(ss)
        ss = tasklist.readline()
    if tasks == '' and config.PlannerConfig.TomorrowChecking == config.LOGFILE_CHECKING['STRICT']:
        raise TomorrowIsEmptyError("The tomorrow section is blank. Do you want to add some tasks for tomorrow?")
    while ss != '':
        tasklist_nextday.write(ss)
        ss = tasklist.readline()
    tasklist_nextday.seek(0)
    tasklist.seek(0)
    tasklist.truncate(0)
    tasklist.write(tasklist_nextday.read())
    tasklist.seek(0)
    tasks = tasks.strip('\n')
    return tasks


def build_period_template(next_day, title, entry, agenda, periodname, checkpointsfile, periodicfile):
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    template = ""
    if title:
        template = title
        template += "\n"
    if entry:
        template += entry
        template += "\n"
    template += "CHECKPOINTS:\n"
    for line in checkpointsfile:
        if line[:3] == '[ ]':
            template += line
    template += "\n"
    template += "AGENDA:\n"
    if agenda:
        template += agenda
        template += "\n"
    template += "\n"
    template += periodname
    for line in periodicfile:
        if line[:3] == '[ ]':
            template += line
    template += "\n"
    template += "NOTES:\n\n\n"
    template += "TIME SPENT ON PLANNER: "
    return template


def build_year_template(planner, next_day, yearfile):
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    title = "= %d =\n" % year
    entry = "\t%s [[%s %d]]\n" % (config.PlannerConfig.PreferredBulletChar, utils.quarter_for_month(month), year)
    periodname = "YEARLYs:\n"
    agenda = ""
    monthtemplate = build_period_template(next_day, title, entry, agenda, periodname, planner.checkpoints_year_file, planner.periodic_year_file)
    return monthtemplate


def build_quarter_template(planner, next_day, quarterfile):
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    title = "= %s %d =\n" % (utils.quarter_for_month(month), year)
    entry = "\t%s [[Month of %s, %d]]\n" % (config.PlannerConfig.PreferredBulletChar, month, year)
    periodname = "QUARTERLYs:\n"
    agenda = ""
    monthtemplate = build_period_template(next_day, title, entry, agenda, periodname, planner.checkpoints_quarter_file, planner.periodic_quarter_file)
    return monthtemplate


def build_month_template(planner, next_day, monthfile):
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    title = "= %s %d =\n" % (month.upper(), year)
    entry = "\t%s [[Week of %s %d, %d]]\n" % (config.PlannerConfig.PreferredBulletChar, month, date, year)
    periodname = "MONTHLYs:\n"
    agenda = ""
    monthtemplate = build_period_template(next_day, title, entry, agenda, periodname, planner.checkpoints_month_file, planner.periodic_month_file)
    return monthtemplate


def build_week_template(planner, next_day, weekfile):
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    title = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
    if utils.PlannerUserSettings.WeekTheme:
        title += "\n"
        title += "Theme: *WEEK OF %s*\n" % utils.PlannerUserSettings.WeekTheme.upper()
    entry = "\t%s [[%s %d, %d]]\n" % (config.PlannerConfig.PreferredBulletChar, month, date, year)
    periodname = "WEEKLYs:\n"
    agenda = ""
    weektemplate = build_period_template(next_day, title, entry, agenda, periodname, planner.checkpoints_week_file, planner.periodic_week_file)
    return weektemplate


def get_theme_for_the_day(daythemes_file, day):
    dailythemes = daythemes_file.read().lower()
    theme = dailythemes[dailythemes.index(day.lower()):]
    theme = theme[theme.index(':'):].strip(': ')
    theme = theme[:theme.index('\n')].strip().upper()
    theme = "*" + theme + "*"
    if len(theme) > 2:
        return theme


def build_day_template(planner, next_day, dayfile):
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    title = ("= %s %s %d, %d =\n" % (day, month[:3], date, year)).upper()

    theme = get_theme_for_the_day(planner.daythemesfile, day)
    if theme:
        title += "\n"
        title += "Theme: %s\n" % theme
    entry = None
    periodicname = "DAILYs:\n"
    undone = do_post_mortem(dayfile)['undone']
    scheduled = scheduling.get_scheduled_tasks(planner.tasklistfile, next_day)
    tomorrow = get_tasks_for_tomorrow(planner.tasklistfile)
    agenda = ''
    if scheduled:
        agenda += scheduled
    if undone:
        if agenda:
            agenda += '\n' + undone
        else:
            agenda += undone
    if tomorrow:
        if agenda:
            agenda += '\n' + tomorrow
        else:
            agenda += tomorrow
    nextdow = next_day.strftime('%A')
    if nextdow.lower() in ('saturday', 'sunday'):
        checkpointsfile = planner.checkpoints_weekend_file
    else:
        checkpointsfile = planner.checkpoints_weekday_file
    daytemplate = build_period_template(next_day, title, entry, agenda, periodicname, checkpointsfile, planner.periodic_day_file)
    return daytemplate


def write_new_template(planner, period, next_day):
    if period == utils.PlannerPeriod.Day:
        template = build_day_template(planner, next_day, planner.dayfile)
        planner.dayfile = StringIO(template)
    if period == utils.PlannerPeriod.Week:
        template = build_week_template(planner, next_day, planner.weekfile)
        planner.weekfile = StringIO(template)
    if period == utils.PlannerPeriod.Month:
        template = build_month_template(planner, next_day, planner.monthfile)
        planner.monthfile = StringIO(template)
    if period == utils.PlannerPeriod.Quarter:
        template = build_quarter_template(planner, next_day, planner.quarterfile)
        planner.quarterfile = StringIO(template)
    if period == utils.PlannerPeriod.Year:
        template = build_year_template(planner, next_day, planner.yearfile)
        planner.yearfile = StringIO(template)


def write_existing_year_template(next_day, yearfile):
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    yearcontents = yearfile.read()
    last_quarter_entry = 'Q'
    previdx = yearcontents.find(last_quarter_entry)
    idx = yearcontents.rfind('\n', 0, previdx)
    newyearcontents = yearcontents[:idx + 1] + '\t%s [[%s %d]]\n' % (config.PlannerConfig.PreferredBulletChar, utils.quarter_for_month(month), year) + yearcontents[idx + 1:]
    return newyearcontents


def write_existing_quarter_template(next_day, quarterfile):
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    quartercontents = quarterfile.read()
    last_month_entry = 'Month of'
    previdx = quartercontents.find(last_month_entry)
    idx = quartercontents.rfind('\n', 0, previdx)
    newquartercontents = quartercontents[:idx + 1] + '\t%s [[Month of %s, %d]]\n' % (config.PlannerConfig.PreferredBulletChar, month, year) + quartercontents[idx + 1:]
    return newquartercontents


def write_existing_month_template(next_day, monthfile):
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    monthcontents = monthfile.read()
    last_week_entry = 'Week of'
    previdx = monthcontents.find(last_week_entry)
    idx = monthcontents.rfind('\n', 0, previdx)
    newmonthcontents = monthcontents[:idx + 1] + '\t%s [[Week of %s %d, %d]]\n' % (config.PlannerConfig.PreferredBulletChar, month, date, year) + monthcontents[idx + 1:]
    return newmonthcontents


def write_existing_week_template(next_day, weekfile):
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    weekcontents = weekfile.read()
    previous_day = next_day - datetime.timedelta(days=1)
    (dateprev, dayprev, monthprev, yearprev) = (previous_day.day, previous_day.strftime('%A'), previous_day.strftime('%B'), previous_day.year)
    previous_day_entry = '%s %d, %d' % (monthprev, dateprev, yearprev)
    previdx = weekcontents.find(previous_day_entry)
    idx = weekcontents.rfind('\n', 0, previdx)
    newweekcontents = weekcontents[:idx+1] + '\t%s [[%s %d, %d]]\n' % (config.PlannerConfig.PreferredBulletChar, month, date, year) + weekcontents[idx + 1:]
    return newweekcontents


def write_existing_template(planner, current_period, next_day):
    # if period is DAY, nop
    if current_period == utils.PlannerPeriod.Day:
        return
    if current_period == utils.PlannerPeriod.Week:
        template = write_existing_week_template(next_day, planner.weekfile)
        planner.weekfile = StringIO(template)
    if current_period == utils.PlannerPeriod.Month:
        template = write_existing_month_template(next_day, planner.monthfile)
        planner.monthfile = StringIO(template)
    if current_period == utils.PlannerPeriod.Quarter:
        template = write_existing_quarter_template(next_day, planner.quarterfile)
        planner.quarterfile = StringIO(template)
    if current_period == utils.PlannerPeriod.Year:
        template = write_existing_year_template(next_day, planner.yearfile)
        planner.yearfile = StringIO(template)
