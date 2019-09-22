import calendar
import datetime
import re

from ...errors import (
    BlockedTaskNotScheduledError,
    DateFormatError,
    LogfileLayoutError,
    RelativeDateError,
    SchedulingDateError,
    ScheduledTaskParsingError,
)
from ...timeperiod import get_next_day, Day, Week, Month
from .primitives import (
    get_entries,
    read_section,
    is_scheduled_task,
    parse_task,
)

SCHEDULED_DATE_PATTERN = re.compile(r"\[\$?([^\[\$]*)\$?\]$")


def get_month_number(monthname):
    """ Get the calendar number corresponding to the month of the year.

    :param str monthname: The name of the month
    :returns int: The number of the month
    """
    month_name_to_number = dict(
        (v.lower(), k) for k, v in enumerate(calendar.month_name)
    )
    return month_name_to_number[monthname.lower()]


def get_month_name(monthnumber):
    """ Get the name of the month corresponding to a calendar month number.

    :param int monthnumber: The number of the month
    :returns str: The name of the month
    """
    month_number_to_name = dict(
        (k, v) for k, v in enumerate(calendar.month_name)
    )
    return month_number_to_name[monthnumber]


def get_appropriate_year(month, day, reference_date):
    """ For date formats where the year is unspecified, determine the
    appropriate year by ensuring that the resulting date is in the future.

    :param int month: Indicated month
    :param int day: Indicated day
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns int: The appropriate year for the date
    """
    # if current year would result in negative, then use next year,
    # otherwise current year
    date_thisyear = datetime.date(reference_date.year, month, day)
    if date_thisyear < reference_date:
        return reference_date.year + 1
    else:
        return reference_date.year


def date_to_string(date, period):
    """
    For each time period define a "standard format" for the date string
    representation that unambiguously represents the date.

    :param :class:`datetime.date` date: A date
    :param :class:`~composer.timeperiod.Period` period: The relevant time
        period for this date
    :returns str: a "standard format" string representing the provided date
        for the relevant time period
    """
    if period == Day:
        date_string = "%s %s, %s" % (get_month_name(date.month), date.day, date.year)
    elif period == Week:
        date_string = "WEEK OF %s %s, %s" % (get_month_name(date.month).upper(), date.day, date.year)
    else:
        date_string = "%s %s" % (get_month_name(date.month), date.year)
    return date_string.upper()


def string_to_date(datestr, reference_date=None):
    """ Parse a given string representing a date.

    Tries various acceptable date formats until one works.

    :param str datestr: A string representing a follow-up date for a
        blocked/scheduled item
    :param :class:`datetime.date` reference_date: Reference date to use in
        parsing the indicated scheduled date
    :returns :class:`datetime.date`: A python date object
    """
    date = None
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
        period = Day
    elif dateformat2.search(datestr):
        (day, month, year) = dateformat2.search(datestr).groups()
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        period = Day
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
        period = Day
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
        period = Day
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
        period = Week
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
        period = Week
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
        period = Week
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
        period = Week
    elif dateformat9.search(datestr):
        (month, year) = dateformat9.search(datestr).groups()
        day = str(1)
        date = datetime.datetime.strptime(
            month + "-" + day + "-" + year, "%B-%d-%Y"
        ).date()
        period = Month
    elif dateformat13.search(datestr):  # TOMORROW
        if not reference_date:
            raise RelativeDateError(
                "Relative date found, but no context available"
            )
        date = get_next_day(reference_date)
        (month, day, year) = (
            get_month_name(date.month).upper(),
            str(date.day),
            str(date.year),
        )
        period = Day
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
        period = Day
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
        period = Day
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
        period = Month
    elif dateformat11.search(datestr):
        (monthn, dayn, yearn) = map(int, dateformat11.search(datestr).groups())
        (month, day, year) = (
            get_month_name(monthn).upper(),
            str(dayn),
            str(yearn),
        )
        date = datetime.date(yearn, monthn, dayn)
        period = Day
    elif dateformat12.search(datestr):
        (monthn, dayn, yearn) = map(int, dateformat12.search(datestr).groups())
        (month, day, year) = (
            get_month_name(monthn).upper(),
            str(dayn),
            str(yearn),
        )
        date = datetime.date(yearn, monthn, dayn)
        period = Day
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
        period = Week
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
        period = Month
    else:
        raise DateFormatError(
            "Date format does not match any acceptable formats! " + datestr
        )
    if date:
        return date, period
    return None


def sanitize_entry(entry, reference_date=None):
    """ Convert a parsed scheduled task into a standard format.

    :param str entry: The entry with a scheduled date
    :param :class:`datetime.date` reference_date: Reference date to use in
        parsing the indicated scheduled date
    :returns str: The entry, with the scheduled date converted to a standard
        format
    """
    task_header, task_contents = parse_task(entry)
    if SCHEDULED_DATE_PATTERN.search(task_header):
        datestr = SCHEDULED_DATE_PATTERN.search(task_header).groups()[0]
        try:
            matched_date = string_to_date(
                datestr, reference_date
            )
        except SchedulingDateError:
            raise
    else:
        raise BlockedTaskNotScheduledError(
            "No scheduled date for blocked task -- add a date for it: "
            + task_header
        )
    datestr = date_to_string(*matched_date)
    task_header = SCHEDULED_DATE_PATTERN.sub(
        "[$" + datestr + "$]", task_header
    )  # replace with standard format
    task = task_header + task_contents
    return task


def check_scheduled_section_for_errors(tasklistfile):
    """ Check that the tasklist includes a scheduled section and that
    it contains only scheduled tasks.

    :param :class:`io.StringIO` tasklistfile: The tasklist
    """
    section, _ = read_section(tasklistfile, 'SCHEDULED')
    entries = get_entries(section)
    for entry in entries:
        entry_string = entry.splitlines()[0]
        entry_string = (
            entry_string + '\n' if entry.endswith('\n') else entry_string
        )
        if not is_scheduled_task(entry_string):
            raise ScheduledTaskParsingError(
                "Task in SCHEDULED section does not appear to be formatted"
                " correctly: " + entry_string
            )


def check_logfile_for_errors(logfile):
    """ Check that the logfile includes an agenda section.

    :param :class:`io.StringIO` logfile: The log file
    """
    try:
        read_section(logfile, "AGENDA")
    except ValueError:
        raise LogfileLayoutError(
            "No AGENDA section found in today's log file!"
            " Add one and try again."
        )
