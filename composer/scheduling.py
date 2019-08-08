import calendar
import datetime
import re

from . import utils
from .errors import (
    BlockedTaskNotScheduledError,
    DateFormatError,
    LogfileLayoutError,
    RelativeDateError,
    TasklistLayoutError)
from .utils import SECTION_HEADER_PATTERN

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


SCHEDULED_DATE_PATTERN = re.compile('\[\$?([^\[\$]*)\$?\]$')


def get_appropriate_year(month, day, today):
    # if current year would result in negative, then use next year, otherwise current year
    date_thisyear = datetime.date(today.year, month, day)
    if date_thisyear < today:
        return today.year + 1
    else:
        return today.year


def get_date_for_schedule_string(datestr, reference_date=None, now=None):
    """ try various acceptable formats and return the first one that works
    Returns both a specific python date that can be used as well as a 'standard format' date string
    that unambiguously represents the date """
    if not now: now = datetime.datetime.now()
    date = None
    month_name_to_number = dict((v.lower(), k) for k, v in enumerate(calendar.month_name))
    month_number_to_name = dict((k, v) for k, v in enumerate(calendar.month_name))

    def get_month_number(monthname):
        return month_name_to_number[monthname.lower()]

    def get_month_name(monthnumber):
        return month_number_to_name[monthnumber]

    # TODO: change these to annotated regex's
    # MONTH DD, YYYY (w optional space or comma or both)
    dateformat1 = re.compile('^([^\d ]+) (\d\d?)[, ] ?(\d{4})$', re.IGNORECASE)
    # DD MONTH, YYYY (w optional space or comma or both)
    dateformat2 = re.compile('^(\d\d?) ([^\d,]+)[, ] ?(\d{4})$', re.IGNORECASE)
    # MONTH DD
    dateformat3 = re.compile('^([^\d ]+) (\d\d?)$', re.IGNORECASE)
    # DD MONTH
    dateformat4 = re.compile('^(\d\d?) ([^\d]+)$', re.IGNORECASE)
    # WEEK OF MONTH DD, YYYY (w optional space or comma or both)
    dateformat5 = re.compile('^WEEK OF ([^\d ]+) (\d\d?)[, ] ?(\d{4})$', re.IGNORECASE)
    # WEEK OF DD MONTH, YYYY (w optional space or comma or both)
    dateformat6 = re.compile('^WEEK OF (\d\d?) ([^\d,]+)[, ] ?(\d{4})$', re.IGNORECASE)
    # WEEK OF MONTH DD
    dateformat7 = re.compile('^WEEK OF ([^\d ]+) (\d\d?)$', re.IGNORECASE)
    # WEEK OF DD MONTH
    dateformat8 = re.compile('^WEEK OF (\d\d?) ([^\d,]+)$', re.IGNORECASE)
    # MONTH YYYY (w optional space or comma or both)
    dateformat9 = re.compile('^([^\d, ]+)[, ] ?(\d{4})$', re.IGNORECASE)
    # MONTH
    dateformat10 = re.compile('^([^\d ]+)$', re.IGNORECASE)
    # MM/DD/YYYY
    dateformat11 = re.compile('^(\d\d)/(\d\d)/(\d\d\d\d)$', re.IGNORECASE)
    # MM-DD-YYYY
    dateformat12 = re.compile('^(\d\d)-(\d\d)-(\d\d\d\d)$', re.IGNORECASE)
    # TOMORROW
    dateformat13 = re.compile('^TOMORROW$', re.IGNORECASE)
    # TODO: need a function to test date boundary status and return monthboundary, weekboundary, or dayboundary (default)
    # NEXT WEEK
    dateformat14 = re.compile('^NEXT WEEK$', re.IGNORECASE)
    # NEXT MONTH
    dateformat15 = re.compile('^NEXT MONTH$', re.IGNORECASE)
    # <DOW>
    dateformat16 = re.compile('^(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)$', re.IGNORECASE)
    # <DOW> (abbrv.)
    dateformat17 = re.compile('^(MON|TUE|WED|THU|FRI|SAT|SUN)$', re.IGNORECASE)

    if dateformat1.search(datestr):
        (month, day, year) = dateformat1.search(datestr).groups()
        date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%B-%d-%Y').date()
        datestr_std = '%s %s, %s' % (month, day, year)
    elif dateformat2.search(datestr):
        (day, month, year) = dateformat2.search(datestr).groups()
        date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%B-%d-%Y').date()
        datestr_std = '%s %s, %s' % (month, day, year)
    elif dateformat3.search(datestr):
        if not reference_date:
            raise RelativeDateError("Relative date found, but no context available")
        (month, day) = dateformat3.search(datestr).groups()
        (monthn, dayn) = (get_month_number(month), int(day))
        year = str(get_appropriate_year(monthn, dayn, reference_date))
        date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%B-%d-%Y').date()
        datestr_std = '%s %s, %s' % (month, day, year)
    elif dateformat4.search(datestr):
        if not reference_date:
            raise RelativeDateError("Relative date found, but no context available")
        (day, month) = dateformat4.search(datestr).groups()
        (monthn, dayn) = (get_month_number(month), int(day))
        year = str(get_appropriate_year(monthn, dayn, reference_date))
        date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%B-%d-%Y').date()
        datestr_std = '%s %s, %s' % (month, day, year)
    elif dateformat5.search(datestr):
        # std = Week of Month dd(sunday/1), yyyy
        (month, day, year) = dateformat5.search(datestr).groups()
        (monthn, dayn, yearn) = (get_month_number(month), int(day), int(year))
        date = datetime.date(yearn, monthn, dayn)
        dow = date.strftime('%A')
        if dayn != 1:
            while dow.lower() != 'sunday':
                date = date - datetime.timedelta(days=1)
                dow = date.strftime('%A')
        (month, day, year) = (get_month_name(date.month), str(date.day), str(date.year))
        date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%B-%d-%Y').date()
        datestr_std = 'WEEK OF %s %s, %s' % (month.upper(), day, year)
    elif dateformat6.search(datestr):
        (day, month, year) = dateformat6.search(datestr).groups()
        (monthn, dayn, yearn) = (get_month_number(month), int(day), int(year))
        date = datetime.date(yearn, monthn, dayn)
        dow = date.strftime('%A')
        if dayn != 1:
            while dow.lower() != 'sunday':
                date = date - datetime.timedelta(days=1)
                dow = date.strftime('%A')
        (month, day, year) = (get_month_name(date.month), str(date.day), str(date.year))
        date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%B-%d-%Y').date()
        datestr_std = 'WEEK OF %s %s, %s' % (month.upper(), day, year)
    elif dateformat7.search(datestr):
        if not reference_date:
            raise RelativeDateError("Relative date found, but no context available")
        (month, day) = dateformat7.search(datestr).groups()
        (monthn, dayn) = (get_month_number(month), int(day))
        yearn = get_appropriate_year(monthn, dayn, reference_date)
        year = str(yearn)
        date = datetime.date(yearn, monthn, dayn)
        dow = date.strftime('%A')
        if dayn != 1:
            while dow.lower() != 'sunday':
                date = date - datetime.timedelta(days=1)
                dow = date.strftime('%A')
        (month, day, year) = (get_month_name(date.month), str(date.day), str(date.year))
        date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%B-%d-%Y').date()
        datestr_std = 'WEEK OF %s %s, %s' % (month.upper(), day, year)
    elif dateformat8.search(datestr):
        if not reference_date:
            raise RelativeDateError("Relative date found, but no context available")
        (day, month) = dateformat8.search(datestr).groups()
        (monthn, dayn) = (get_month_number(month), int(day))
        yearn = get_appropriate_year(monthn, dayn, reference_date)
        year = str(yearn)
        date = datetime.date(yearn, monthn, dayn)
        dow = date.strftime('%A')
        if dayn != 1:
            while dow.lower() != 'sunday':
                date = date - datetime.timedelta(days=1)
                dow = date.strftime('%A')
        (month, day, year) = (get_month_name(date.month), str(date.day), str(date.year))
        date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%B-%d-%Y').date()
        datestr_std = 'WEEK OF %s %s, %s' % (month.upper(), day, year)
    elif dateformat9.search(datestr):
        (month, year) = dateformat9.search(datestr).groups()
        day = str(1)
        date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%B-%d-%Y').date()
        datestr_std = '%s %s' % (month, year)
    elif dateformat13.search(datestr):  # TOMORROW
        if not reference_date:
            raise RelativeDateError("Relative date found, but no context available")
        date = utils.get_next_day(reference_date)
        (month, day, year) = (get_month_name(date.month).upper(), str(date.day), str(date.year))
        datestr_std = '%s %s, %s' % (month, day, year)
    elif dateformat16.search(datestr):  # <DOW> e.g. MONDAY
        if not reference_date:
            raise RelativeDateError("Relative date found, but no context available")
        dowToSchedule = dateformat16.search(datestr).groups()[0]
        upcomingweek = [reference_date + datetime.timedelta(days=d) for d in range(1, 8)]
        dow = [d.strftime('%A').upper() for d in upcomingweek]
        date = upcomingweek[dow.index(dowToSchedule)]
        (month, day, year) = (get_month_name(date.month).upper(), str(date.day), str(date.year))
        datestr_std = '%s %s, %s' % (month, day, year)
    elif dateformat17.search(datestr):  # <DOW> short e.g. MON
        if not reference_date:
            raise RelativeDateError("Relative date found, but no context available")
        dowToSchedule = dateformat17.search(datestr).groups()[0]
        upcomingweek = [reference_date + datetime.timedelta(days=d) for d in range(1, 8)]
        dow = [d.strftime('%a').upper() for d in upcomingweek]
        date = upcomingweek[dow.index(dowToSchedule)]
        (month, day, year) = (get_month_name(date.month).upper(), str(date.day), str(date.year))
        datestr_std = '%s %s, %s' % (month, day, year)
    elif dateformat10.search(datestr):  # MONTH, e.g. DECEMBER
        if not reference_date:
            raise RelativeDateError("Relative date found, but no context available")
        month = dateformat10.search(datestr).groups()[0]
        (monthn, dayn) = (get_month_number(month), 1)
        (day, year) = (str(dayn), str(get_appropriate_year(monthn, dayn, reference_date)))
        date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%B-%d-%Y').date()
        datestr_std = '%s %s' % (month, year)
    elif dateformat11.search(datestr):
        (monthn, dayn, yearn) = map(int, dateformat11.search(datestr).groups())
        (month, day, year) = (get_month_name(monthn).upper(), str(dayn), str(yearn))
        date = datetime.date(yearn, monthn, dayn)
        datestr_std = '%s %s, %s' % (month, day, year)
    elif dateformat12.search(datestr):
        (monthn, dayn, yearn) = map(int, dateformat12.search(datestr).groups())
        (month, day, year) = (get_month_name(monthn).upper(), str(dayn), str(yearn))
        date = datetime.date(yearn, monthn, dayn)
        datestr_std = '%s %s, %s' % (month, day, year)
    elif dateformat14.search(datestr):  # NEXT WEEK
        if not reference_date:
            raise RelativeDateError("Relative date found, but no context available")
        dowToSchedule = 'SUNDAY'  # start of next week
        upcomingweek = [reference_date + datetime.timedelta(days=d) for d in range(1, 8)]
        dow = [d.strftime('%A').upper() for d in upcomingweek]
        date = upcomingweek[dow.index(dowToSchedule)]
        (month, day, year) = (get_month_name(date.month).upper(), str(date.day), str(date.year))
        datestr_std = 'WEEK OF %s %s, %s' % (month.upper(), day, year)
    elif dateformat15.search(datestr):  # NEXT MONTH
        if not reference_date:
            raise RelativeDateError("Relative date found, but no context available")
        upcomingmonth = [reference_date + datetime.timedelta(days=d) for d in range(1, 31)]
        dates = [d.day for d in upcomingmonth]
        date = upcomingmonth[dates.index(1)]
        (month, day, year) = (get_month_name(date.month).upper(), str(date.day), str(date.year))
        datestr_std = '%s %s' % (month, year)
    else:
        raise DateFormatError("Date format does not match any acceptable formats! " + datestr)
    if date:
        return {'date': date, 'datestr': datestr_std.upper()}
    return None


def _process_scheduled_task(taskfile, scheduledtasks, line, reference_date, now):
    """ Convert a parsed scheduled task into a standard format and append it,
    along with any subtasks, to a gathered list of scheduled tasks.
    """
    if SCHEDULED_DATE_PATTERN.search(line):
        datestr = SCHEDULED_DATE_PATTERN.search(line).groups()[0]
        try:
            matcheddate = get_date_for_schedule_string(datestr, reference_date, now)
        except Exception:
            raise
    else:
        raise BlockedTaskNotScheduledError("No scheduled date for blocked task -- add a date for it: " + line)
    line = SCHEDULED_DATE_PATTERN.sub('[$' + matcheddate['datestr'] + '$]', line)  # replace with standard format
    scheduledtasks += line
    line = taskfile.readline()
    while line.startswith('\t'):
        scheduledtasks += line
        line = taskfile.readline()
    return line, scheduledtasks


def _parse_tomorrow_section(line, tasklist, tasklist_tidied):
    tasklist_tidied.write(line)
    line = tasklist.readline()
    while line != '' and not SECTION_HEADER_PATTERN.search(line):
        tasklist_tidied.write(line)
        line = tasklist.readline()
    return line


def _parse_scheduled_section(tasklist, tasklist_tidied, scheduledtasks, line, reference_date, now):
    tasklist_tidied.write(line)
    line = tasklist.readline()
    while line != '' and not SECTION_HEADER_PATTERN.search(line):
        if line.startswith('[o'):
            line, scheduledtasks = _process_scheduled_task(tasklist, scheduledtasks, line, reference_date, now)
        elif line.startswith('\n'):
            tasklist_tidied.write(line)
            line = tasklist.readline()
        else:
            raise BlockedTaskNotScheduledError("Task in SCHEDULED section does not appear to be formatted correctly: " + line)
    return line


def _extract_scheduled_items_from_tasklist(tasklist, reference_date, now):
    tasklist_tidied = StringIO()
    scheduledtasks = ""
    line = tasklist.readline()
    while line != '':
        # ignore tasks in tomorrow since actively scheduled by you
        if line[:len('tomorrow')].lower() == 'tomorrow':
            line = _parse_tomorrow_section(line, tasklist, tasklist_tidied)
        elif line[:len('scheduled')].lower() == 'scheduled':
            line = _parse_scheduled_section(tasklist, tasklist_tidied, scheduledtasks, line, reference_date, now)
        elif line.startswith('[o'):
            line, scheduledtasks = _process_scheduled_task(tasklist, scheduledtasks, line, reference_date, now)
        else:
            tasklist_tidied.write(line)
            line = tasklist.readline()
    tasklist_tidied.seek(0)
    return scheduledtasks, tasklist_tidied


def _extract_scheduled_items_from_logfile(logfile, scheduledtasks, reference_date, now):
    # go through a log file (e.g. today's log file)
    # if [o] then make sure [$$] and parseable
    # move to scheduled
    line = logfile.readline()
    while line != '' and line[:len('agenda')].lower() != 'agenda':
        line = logfile.readline()
    if line == '':
        raise LogfileLayoutError("No AGENDA section found in today's log file! Add one and try again.")
    line = logfile.readline()
    while line != '' and not SECTION_HEADER_PATTERN.search(line):
        if line.startswith('[o'):
            line, scheduledtasks = _process_scheduled_task(logfile, scheduledtasks, line, reference_date, now)
        else:
            line = logfile.readline()
    return scheduledtasks


def _add_scheduled_tasks_to_tasklist(tasklist, scheduledtasks):
    """ Find SCHEDULED section and insert scheduled tasks.
    This disregards any contents of the SCHEDULED section in the tasklist
    and simply places the provided scheduled tasks in that section of
    the tasklist. Any scheduled items in the tasklist should already have
    been extracted into the scheduled tasks provided to this function.
    """
    tasklist_tidied = StringIO()
    line = tasklist.readline()
    while line != '' and line[:len('scheduled')].lower() != 'scheduled':
        tasklist_tidied.write(line)
        line = tasklist.readline()
    if line == '':
        raise TasklistLayoutError("Tasklist SCHEDULED section not found!")
    tasklist_tidied.write(line)

    tasklist_tidied.write(scheduledtasks)

    line = tasklist.readline()
    while line != '':
        tasklist_tidied.write(line)
        line = tasklist.readline()

    tasklist_tidied.seek(0)
    return tasklist_tidied


def schedule_tasks(planner, now=None):
    """ 1. Go through the Tasklist till SCHEDULED section found
    2. If task is marked as scheduled/blocked (i.e. "[o]"), then make sure a
    follow-up date is indicated (via "[$<date>$]") and that it is parseable
    3. move to bottom of scheduled
    4. loop through all scheduled till naother section found or eof
    5. go through any other section
    """
    if not now:
        now = datetime.datetime.now()

    scheduledtasks, tasklist = _extract_scheduled_items_from_tasklist(planner.tasklistfile, planner.date, now)  # tasklist - scheduled tasks

    scheduledtasks = _extract_scheduled_items_from_logfile(planner.dayfile, scheduledtasks, planner.date, now)

    tasklist = _add_scheduled_tasks_to_tasklist(tasklist, scheduledtasks)

    planner.tasklistfile = tasklist


def get_scheduled_tasks(tasklist, for_day):
    # look at SCHEDULED section in tasklist and return if scheduled for supplied day
    # remove from tasklist
    # Note: schedule tasks should already have been performed on previous day to migrate those tasks to the tasklist
    tasklist_updated = StringIO()
    line = tasklist.readline()
    while line != '' and line[:len('scheduled')].lower() != 'scheduled':
        tasklist_updated.write(line)
        line = tasklist.readline()
    tasklist_updated.write(line)
    if line == '':
        raise TasklistLayoutError("No SCHEDULED section found in TaskList!")
    scheduledtasks = ''
    line = tasklist.readline()
    while line != '' and not SECTION_HEADER_PATTERN.search(line):
        if line.startswith('[o'):
            if SCHEDULED_DATE_PATTERN.search(line):
                datestr = SCHEDULED_DATE_PATTERN.search(line).groups()[0]
                try:
                    matcheddate = get_date_for_schedule_string(datestr)
                except Exception:
                    raise
                if for_day >= matcheddate['date']:
                    scheduledtasks += line
                    line = tasklist.readline()
                    while line.startswith('\t'):
                        scheduledtasks += line
                        line = tasklist.readline()
                else:
                    tasklist_updated.write(line)
                    line = tasklist.readline()
            else:
                raise BlockedTaskNotScheduledError('Scheduled task has no date!' + line)
        else:
            tasklist_updated.write(line)
            line = tasklist.readline()
    # copy rest of the file
    while line != '':
        tasklist_updated.write(line)
        line = tasklist.readline()

    tasklist_updated.seek(0)
    scheduledtasks = scheduledtasks.strip('\n')
    return scheduledtasks, tasklist_updated
