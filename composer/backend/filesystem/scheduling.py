import re

from ...errors import (
    BlockedTaskNotScheduledError,
    DateFormatError,
    LogfileLayoutError,
    SchedulingDateError,
)
from ...timeperiod import (
    Week,
    Month,
    Quarter,
    Year,
    Eternity,
    quarter_for_month,
    get_month_name,
)
from .primitives import read_section, parse_task
from .date_parsers import (
    dateformat1,
    dateformat2,
    dateformat3,
    dateformat4,
    dateformat5,
    dateformat6,
    dateformat7,
    dateformat8,
    dateformat9,
    dateformat10,
    dateformat11,
    dateformat12,
    dateformat13,
    dateformat14,
    dateformat15,
    dateformat16,
    dateformat17,
    dateformat18,
    dateformat19,
    dateformat20,
    dateformat21,
    dateformat22,
    dateformat23,
    dateformat24,
    dateformat25,
    dateformat26,
    dateformat27,
    dateformat28,
    parse_dateformat1,
    parse_dateformat2,
    parse_dateformat3,
    parse_dateformat4,
    parse_dateformat5,
    parse_dateformat6,
    parse_dateformat7,
    parse_dateformat8,
    parse_dateformat9,
    parse_dateformat10,
    parse_dateformat11,
    parse_dateformat12,
    parse_dateformat13,
    parse_dateformat14,
    parse_dateformat15,
    parse_dateformat16,
    parse_dateformat17,
    parse_dateformat18,
    parse_dateformat19,
    parse_dateformat20,
    parse_dateformat21,
    parse_dateformat22,
    parse_dateformat23,
    parse_dateformat24,
    parse_dateformat25,
    parse_dateformat26,
    parse_dateformat27,
    parse_dateformat28,
)

SCHEDULED_DATE_PATTERN = re.compile(r"\[\$?([^\[\$]*)\$?\]$")


def date_to_string(date, period):
    """
    For each time period define a "standard format" for the date string
    representation that unambiguously represents the date. This simply produces
    the appropriate string representation for the given date and time period
    does NOT check actual period boundary conditions.

    :param :class:`datetime.date` date: A date
    :param :class:`~composer.timeperiod.Period` period: The relevant time
        period for this date
    :returns str: a "standard format" string representing the provided date
        for the relevant time period
    """
    if period == Week:
        date_string = "WEEK OF %s %s, %s" % (
            get_month_name(date.month).upper(),
            date.day,
            date.year,
        )
    elif period == Month:
        date_string = "%s %s" % (get_month_name(date.month), date.year)
    elif period == Quarter:
        quarter = quarter_for_month(date.month)
        date_string = "{} {}".format(quarter, date.year)
    elif period == Year:
        date_string = "{}".format(date.year)
    elif period == Eternity:
        date_string = "SOMEDAY"
    else:
        # default to Day
        date_string = "%s %s, %s" % (
            get_month_name(date.month),
            date.day,
            date.year,
        )
    return date_string.upper()


def string_to_date(datestr, reference_date=None):
    """Parse a given string representing a date.

    Tries various acceptable date formats until one works.

    :param str datestr: A string representing a follow-up date for a
        blocked/scheduled item
    :param :class:`datetime.date` reference_date: Reference date to use in
        parsing the indicated scheduled date
    :returns tuple: A python date object, and the relevant time period implied
        by the string representation
    """
    patterns = (
        (dateformat28, parse_dateformat28),
        (dateformat27, parse_dateformat27),
        (dateformat26, parse_dateformat26),
        (dateformat1, parse_dateformat1),
        (dateformat2, parse_dateformat2),
        (dateformat18, parse_dateformat18),
        (dateformat3, parse_dateformat3),
        (dateformat4, parse_dateformat4),
        (dateformat5, parse_dateformat5),
        (dateformat6, parse_dateformat6),
        (dateformat7, parse_dateformat7),
        (dateformat8, parse_dateformat8),
        (dateformat9, parse_dateformat9),
        (dateformat13, parse_dateformat13),
        (dateformat25, parse_dateformat25),
        (dateformat16, parse_dateformat16),
        (dateformat17, parse_dateformat17),
        (dateformat11, parse_dateformat11),
        (dateformat12, parse_dateformat12),
        (dateformat14, parse_dateformat14),
        (dateformat15, parse_dateformat15),
        (dateformat19, parse_dateformat19),
        (dateformat23, parse_dateformat23),
        (dateformat24, parse_dateformat24),
        (dateformat21, parse_dateformat21),
        (dateformat22, parse_dateformat22),
        (dateformat20, parse_dateformat20),
        (dateformat10, parse_dateformat10),
    )

    for pattern, parse in patterns:
        if pattern.search(datestr):
            return parse(datestr, reference_date)

    raise DateFormatError(
        "Date format does not match any acceptable formats! " + datestr
    )


def standardize_entry_date(entry, reference_date=None):
    """Convert a parsed scheduled task into a standard format. In addition to
    providing uniformity, this also contextualizes dates that may have been
    relatively specified so that it is unambiguous and time-invariant (e.g.
    dates like "next week").

    :param str entry: The entry with a scheduled date
    :param :class:`datetime.date` reference_date: Reference date to use in
        parsing the indicated scheduled date
    :returns str: The entry, with the scheduled date converted to a standard
        format
    """
    task_header, task_contents = parse_task(entry)
    matched_date = get_due_date(task_header, reference_date)
    datestr = date_to_string(*matched_date)
    task_header = SCHEDULED_DATE_PATTERN.sub(
        "[$" + datestr + "$]", task_header
    )  # replace with standard format
    task = task_header + task_contents
    return task


def get_due_date(task, reference_date=None):
    """Get the due date for a task.

    :param str task: The task
    :param :class:`datetime.date` reference_date: A reference date to use
        in case the due date is specified relatively
    :returns tuple: The due date, together with the implied period
        for the date
    """
    header, _ = parse_task(task)
    if not SCHEDULED_DATE_PATTERN.search(header):
        raise BlockedTaskNotScheduledError(
            "No scheduled date for blocked task -- add a date for it:\n"
            + header
        )
    datestr = SCHEDULED_DATE_PATTERN.search(header).groups()[0]
    try:
        matched_date, period = string_to_date(datestr, reference_date)
    except SchedulingDateError:
        raise
    return matched_date, period


def is_task_due(task, for_day):
    """Check if the task is due (or past due) on the specified day.

    :param str task: The task
    :param :class:`datetime.date` for_day: The date
    :returns bool: Whether the task is due
    """
    date, _ = get_due_date(task)
    return for_day >= date


def check_logfile_for_errors(logfile):
    """Check that the logfile includes an agenda section.

    :param :class:`io.StringIO` logfile: The log file
    """
    try:
        read_section(logfile, "AGENDA")
    except ValueError:
        raise LogfileLayoutError(
            "No AGENDA section found in today's log file!"
            " Add one and try again."
        )
