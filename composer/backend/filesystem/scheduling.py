import calendar
import datetime
import re

from ... import utils  # TODO: eliminate this dependency
from ...errors import (
    BlockedTaskNotScheduledError,
    DateFormatError,
    LogfileLayoutError,
    RelativeDateError,
    SchedulingDateError,
    ScheduledTaskParsingError,
    TasklistLayoutError,
)
from .utils import (
    SECTION_PATTERN,
    add_to_section,
    get_section_pattern,
    get_task_items,
    is_scheduled_task,
    is_subtask,
    item_list_to_string,
    make_file,
    read_section,
    partition_at,
    partition_items,
)

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


SCHEDULED_DATE_PATTERN = re.compile(r"\[\$?([^\[\$]*)\$?\]$")


def get_appropriate_year(month, day, today):
    # if current year would result in negative, then use next year,
    # otherwise current year
    date_thisyear = datetime.date(today.year, month, day)
    if date_thisyear < today:
        return today.year + 1
    else:
        return today.year


def get_date_for_schedule_string(datestr, reference_date=None):
    """ try various acceptable formats and return the first one that works
    Returns both a specific python date that can be used as well as a
    'standard format' date string that unambiguously represents the date
    """
    date = None
    month_name_to_number = dict(
        (v.lower(), k) for k, v in enumerate(calendar.month_name)
    )
    month_number_to_name = dict(
        (k, v) for k, v in enumerate(calendar.month_name)
    )

    def get_month_number(monthname):
        return month_name_to_number[monthname.lower()]

    def get_month_name(monthnumber):
        return month_number_to_name[monthnumber]

    # TODO: change these to annotated regex's
    # MONTH DD, YYYY (w optional space or comma or both)
    dateformat1 = re.compile(
        r"^([^\d ]+) (\d\d?)[, ] ?(\d{4})$", re.IGNORECASE
    )
    # DD MONTH, YYYY (w optional space or comma or both)
    dateformat2 = re.compile(
        r"^(\d\d?) ([^\d,]+)[, ] ?(\d{4})$", re.IGNORECASE
    )
    # MONTH DD
    dateformat3 = re.compile(r"^([^\d ]+) (\d\d?)$", re.IGNORECASE)
    # DD MONTH
    dateformat4 = re.compile(r"^(\d\d?) ([^\d]+)$", re.IGNORECASE)
    # WEEK OF MONTH DD, YYYY (w optional space or comma or both)
    dateformat5 = re.compile(
        r"^WEEK OF ([^\d ]+) (\d\d?)[, ] ?(\d{4})$", re.IGNORECASE
    )
    # WEEK OF DD MONTH, YYYY (w optional space or comma or both)
    dateformat6 = re.compile(
        r"^WEEK OF (\d\d?) ([^\d,]+)[, ] ?(\d{4})$", re.IGNORECASE
    )
    # WEEK OF MONTH DD
    dateformat7 = re.compile(r"^WEEK OF ([^\d ]+) (\d\d?)$", re.IGNORECASE)
    # WEEK OF DD MONTH
    dateformat8 = re.compile(r"^WEEK OF (\d\d?) ([^\d,]+)$", re.IGNORECASE)
    # MONTH YYYY (w optional space or comma or both)
    dateformat9 = re.compile(r"^([^\d, ]+)[, ] ?(\d{4})$", re.IGNORECASE)
    # MONTH
    dateformat10 = re.compile(r"^([^\d ]+)$", re.IGNORECASE)
    # MM/DD/YYYY
    dateformat11 = re.compile(r"^(\d\d)/(\d\d)/(\d\d\d\d)$", re.IGNORECASE)
    # MM-DD-YYYY
    dateformat12 = re.compile(r"^(\d\d)-(\d\d)-(\d\d\d\d)$", re.IGNORECASE)
    # TOMORROW
    dateformat13 = re.compile(r"^TOMORROW$", re.IGNORECASE)
    # TODO: need a function to test date boundary status and return
    # monthboundary, weekboundary, or dayboundary (default)
    # NEXT WEEK
    dateformat14 = re.compile(r"^NEXT WEEK$", re.IGNORECASE)
    # NEXT MONTH
    dateformat15 = re.compile(r"^NEXT MONTH$", re.IGNORECASE)
    # <DOW>
    dateformat16 = re.compile(
        r"^(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)$",
        re.IGNORECASE,
    )
    # <DOW> (abbrv.)
    dateformat17 = re.compile(
        r"^(MON|TUE|WED|THU|FRI|SAT|SUN)$", re.IGNORECASE
    )

    if dateformat1.search(datestr):
        (month, day, year) = dateformat1.search(datestr).groups()
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        datestr_std = "%s %s, %s" % (month, day, year)
    elif dateformat2.search(datestr):
        (day, month, year) = dateformat2.search(datestr).groups()
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        datestr_std = "%s %s, %s" % (month, day, year)
    elif dateformat3.search(datestr):
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        (month, day) = dateformat3.search(datestr).groups()
        (monthn, dayn) = (get_month_number(month), int(day))
        year = str(get_appropriate_year(monthn, dayn, reference_date))
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        datestr_std = "%s %s, %s" % (month, day, year)
    elif dateformat4.search(datestr):
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        (day, month) = dateformat4.search(datestr).groups()
        (monthn, dayn) = (get_month_number(month), int(day))
        year = str(get_appropriate_year(monthn, dayn, reference_date))
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        datestr_std = "%s %s, %s" % (month, day, year)
    elif dateformat5.search(datestr):
        # std = Week of Month dd(sunday/1), yyyy
        (month, day, year) = dateformat5.search(datestr).groups()
        (monthn, dayn, yearn) = (get_month_number(month), int(day), int(year))
        date = datetime.date(yearn, monthn, dayn)
        dow = date.strftime("%A")
        if dayn != 1:
            while dow.lower() != "sunday":
                date = date - datetime.timedelta(days=1)
                dow = date.strftime("%A")
        (month, day, year) = (
            get_month_name(date.month),
            str(date.day),
            str(date.year),
        )
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        datestr_std = "WEEK OF %s %s, %s" % (month.upper(), day, year)
    elif dateformat6.search(datestr):
        (day, month, year) = dateformat6.search(datestr).groups()
        (monthn, dayn, yearn) = (get_month_number(month), int(day), int(year))
        date = datetime.date(yearn, monthn, dayn)
        dow = date.strftime("%A")
        if dayn != 1:
            while dow.lower() != "sunday":
                date = date - datetime.timedelta(days=1)
                dow = date.strftime("%A")
        (month, day, year) = (
            get_month_name(date.month),
            str(date.day),
            str(date.year),
        )
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        datestr_std = "WEEK OF %s %s, %s" % (month.upper(), day, year)
    elif dateformat7.search(datestr):
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        (month, day) = dateformat7.search(datestr).groups()
        (monthn, dayn) = (get_month_number(month), int(day))
        yearn = get_appropriate_year(monthn, dayn, reference_date)
        year = str(yearn)
        date = datetime.date(yearn, monthn, dayn)
        dow = date.strftime("%A")
        if dayn != 1:
            while dow.lower() != "sunday":
                date = date - datetime.timedelta(days=1)
                dow = date.strftime("%A")
        (month, day, year) = (
            get_month_name(date.month),
            str(date.day),
            str(date.year),
        )
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        datestr_std = "WEEK OF %s %s, %s" % (month.upper(), day, year)
    elif dateformat8.search(datestr):
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        (day, month) = dateformat8.search(datestr).groups()
        (monthn, dayn) = (get_month_number(month), int(day))
        yearn = get_appropriate_year(monthn, dayn, reference_date)
        year = str(yearn)
        date = datetime.date(yearn, monthn, dayn)
        dow = date.strftime("%A")
        if dayn != 1:
            while dow.lower() != "sunday":
                date = date - datetime.timedelta(days=1)
                dow = date.strftime("%A")
        (month, day, year) = (
            get_month_name(date.month),
            str(date.day),
            str(date.year),
        )
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        datestr_std = "WEEK OF %s %s, %s" % (month.upper(), day, year)
    elif dateformat9.search(datestr):
        (month, year) = dateformat9.search(datestr).groups()
        day = str(1)
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        datestr_std = "%s %s" % (month, year)
    elif dateformat13.search(datestr):  # TOMORROW
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        date = utils.get_next_day(reference_date)
        (month, day, year) = (
            get_month_name(date.month).upper(),
            str(date.day),
            str(date.year),
        )
        datestr_std = "%s %s, %s" % (month, day, year)
    elif dateformat16.search(datestr):  # <DOW> e.g. MONDAY
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        dowToSchedule = dateformat16.search(datestr).groups()[0]
        upcomingweek = [
            reference_date + datetime.timedelta(days=d) for d in range(1, 8)
        ]
        dow = [d.strftime("%A").upper() for d in upcomingweek]
        date = upcomingweek[dow.index(dowToSchedule)]
        (month, day, year) = (
            get_month_name(date.month).upper(),
            str(date.day),
            str(date.year),
        )
        datestr_std = "%s %s, %s" % (month, day, year)
    elif dateformat17.search(datestr):  # <DOW> short e.g. MON
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        dowToSchedule = dateformat17.search(datestr).groups()[0]
        upcomingweek = [
            reference_date + datetime.timedelta(days=d) for d in range(1, 8)
        ]
        dow = [d.strftime("%a").upper() for d in upcomingweek]
        date = upcomingweek[dow.index(dowToSchedule)]
        (month, day, year) = (
            get_month_name(date.month).upper(),
            str(date.day),
            str(date.year),
        )
        datestr_std = "%s %s, %s" % (month, day, year)
    elif dateformat10.search(datestr):  # MONTH, e.g. DECEMBER
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        month = dateformat10.search(datestr).groups()[0]
        (monthn, dayn) = (get_month_number(month), 1)
        (day, year) = (
            str(dayn),
            str(get_appropriate_year(monthn, dayn, reference_date)),
        )
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        datestr_std = "%s %s" % (month, year)
    elif dateformat11.search(datestr):
        (monthn, dayn, yearn) = map(int, dateformat11.search(datestr).groups())
        (month, day, year) = (
            get_month_name(monthn).upper(),
            str(dayn),
            str(yearn),
        )
        date = datetime.date(yearn, monthn, dayn)
        datestr_std = "%s %s, %s" % (month, day, year)
    elif dateformat12.search(datestr):
        (monthn, dayn, yearn) = map(int, dateformat12.search(datestr).groups())
        (month, day, year) = (
            get_month_name(monthn).upper(),
            str(dayn),
            str(yearn),
        )
        date = datetime.date(yearn, monthn, dayn)
        datestr_std = "%s %s, %s" % (month, day, year)
    elif dateformat14.search(datestr):  # NEXT WEEK
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        dowToSchedule = "SUNDAY"  # start of next week
        upcomingweek = [
            reference_date + datetime.timedelta(days=d) for d in range(1, 8)
        ]
        dow = [d.strftime("%A").upper() for d in upcomingweek]
        date = upcomingweek[dow.index(dowToSchedule)]
        (month, day, year) = (
            get_month_name(date.month).upper(),
            str(date.day),
            str(date.year),
        )
        datestr_std = "WEEK OF %s %s, %s" % (month.upper(), day, year)
    elif dateformat15.search(datestr):  # NEXT MONTH
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        upcomingmonth = [
            reference_date + datetime.timedelta(days=d) for d in range(1, 31)
        ]
        dates = [d.day for d in upcomingmonth]
        date = upcomingmonth[dates.index(1)]
        (month, day, year) = (
            get_month_name(date.month).upper(),
            str(date.day),
            str(date.year),
        )
        datestr_std = "%s %s" % (month, year)
    else:
        raise DateFormatError(
            "Date format does not match any acceptable formats! " + datestr
        )
    if date:
        return {"date": date, "datestr": datestr_std.upper()}
    return None


def _to_standard_date_format(item, reference_date):
    """ Convert a parsed scheduled task into a standard format. """
    date_string = item.splitlines()[0]
    date_string = date_string + '\n' if item.endswith('\n') else date_string
    if SCHEDULED_DATE_PATTERN.search(date_string):
        datestr = SCHEDULED_DATE_PATTERN.search(date_string).groups()[0]
        try:
            matcheddate = get_date_for_schedule_string(datestr, reference_date)
        except SchedulingDateError:
            raise
    else:
        raise BlockedTaskNotScheduledError(
            "No scheduled date for blocked task -- add a date for it: "
            + date_string
        )
    date_string = SCHEDULED_DATE_PATTERN.sub(
        "[$" + matcheddate["datestr"] + "$]", date_string
    )  # replace with standard format
    return date_string


def _check_scheduled_section_for_errors(planner):
    section, _ = read_section(planner.tasklistfile, 'SCHEDULED')
    items = get_task_items(section)
    for item in items:
        item_string = item.splitlines()[0]
        item_string = (
            item_string + '\n' if item.endswith('\n') else item_string
        )
        if not is_scheduled_task(item_string):
            raise ScheduledTaskParsingError(
                "Task in SCHEDULED section does not appear to be formatted"
                " correctly: " + item_string
            )


def _check_logfile_for_errors(logfile):
    try:
        read_section(logfile, "AGENDA")
    except ValueError:
        raise LogfileLayoutError(
            "No AGENDA section found in today's log file!"
            " Add one and try again."
        )


def schedule_tasks(planner):
    """ 1. Go through the Tasklist till SCHEDULED section found
    2. If task is marked as scheduled/blocked (i.e. "[o]"), then make sure a
    follow-up date is indicated (via "[$<date>$]") and that it is parseable
    3. move to bottom of scheduled
    4. loop through all scheduled till naother section found or eof
    5. go through any other section
    """
    # TODO: add a "diagnostic" function for sections w/ a checker fn
    # to be applied to items
    # (can generalize the existing helper for scheduled section)
    # TODO: keep low-level operations contained in utils -- make/extend
    # additional interfaces as needed
    # TODO: these diagnostics are not covered by tests
    _check_scheduled_section_for_errors(planner)
    _check_logfile_for_errors(planner.dayfile)
    # ignore tasks in tomorrow since actively scheduled by you
    tomorrow, tasklist_no_tomorrow = read_section(
        planner.tasklistfile, 'TOMORROW'
    )
    task_items = get_task_items(tasklist_no_tomorrow)
    tasklist_tasks, tasklist_no_scheduled = partition_items(
        task_items, is_scheduled_task
    )
    # TODO: these interfaces should operate at a high level and translate
    # up/down only at the beginning and end
    tasklist_no_scheduled = make_file(
        item_list_to_string(tasklist_no_scheduled)
    )
    day_tasks = get_task_items(planner.dayfile, of_type=is_scheduled_task)
    tasks = tasklist_tasks + day_tasks
    tasks = [
        (
            _to_standard_date_format(task, planner.date)
            if is_scheduled_task(task)
            else task
        )
        for task in tasks
    ]
    tasks = item_list_to_string(tasks)
    new_file = add_to_section(tasklist_no_scheduled, "SCHEDULED", tasks)
    new_file = add_to_section(
        new_file, "TOMORROW", tomorrow.read()
    )  # add tomorrow tasks back
    planner.tasklistfile = new_file


def get_due_tasks(tasklist, for_day):
    """ Look at the SCHEDULED section of the tasklist and retrive any tasks that
    are due/overdue for the given day (e.g. tomorrow, if preparing tomorrow's
    agenda).

    This only operates on explicitly scheduled tasks, not tasks manually set
    aside for tomorrow or which may happen to be appropriate for the given day
    as determined in some other way (e.g. periodic tasks).

    Note: task scheduling should already have been performed on relevant
    logfiles (like the previous day's) to migrate those tasks to the tasklist.
    """

    def is_task_due(task):
        if not SCHEDULED_DATE_PATTERN.search(task):
            raise BlockedTaskNotScheduledError(
                "Scheduled task has no date!" + task
            )
        datestr = SCHEDULED_DATE_PATTERN.search(task).groups()[0]
        try:
            matcheddate = get_date_for_schedule_string(datestr)
        except SchedulingDateError:
            raise
        return for_day >= matcheddate["date"]

    try:
        scheduled, tasklist_no_scheduled = read_section(tasklist, "scheduled")
    except ValueError:
        raise TasklistLayoutError("No SCHEDULED section found in TaskList!")
    items = get_task_items(scheduled)
    due, not_due = partition_items(items, is_task_due)
    due, not_due = map(item_list_to_string, (due, not_due))
    new_tasklist = add_to_section(tasklist_no_scheduled, 'scheduled', not_due)
    return due, new_tasklist
