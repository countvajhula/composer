import os
from datetime import timedelta
from ...timeperiod import get_next_period, Day
from ...errors import (
    InvalidTimeFormatError,
    LogfileLayoutError,
    LogfileAlreadyExistsError,
)

from .primitives import get_log_filename, read_file, read_section
from .time_parsers import (
    timeformat1,
    timeformat2,
    timeformat3,
    timeformat4,
    parse_timeformat1,
    parse_timeformat2,
    parse_timeformat3,
    parse_timeformat4,
)

try:  # py3
    FileNotFoundError
except NameError:  # py2
    FileNotFoundError = IOError


def get_log_for_date(period, for_date, planner_root):
    """For any date, a time period uniquely maps to a single log file on disk
    for a particular planner instance (which is tied to a wiki root path).
    This function returns that file for the given time period and date.

    That is, this returns the logfile for the specified period that is tracking
    the specified date for the planner at the specified location.

    This is an interface rather than a planner method since it answers a
    question about the historical data tracked at the path managed by the
    planner, rather than the current actionable state of the planner.

    :param :class:`~composer.timeperiod.Period` period: The time period
        for which we want the log file
    :param :class:`datetime.date` for_date: The date of interest
    :param str planner_root: The root path of the planner wiki
    :returns :class:`io.StringIO`: The log file
    """
    if period < Day:
        return None
    start_date = period.get_start_date(for_date)
    log_path = get_log_filename(start_date, period, planner_root)
    try:
        log = read_file(log_path)
    except FileNotFoundError:
        raise
    return log


def string_to_time(time_string):
    """Parse a given string representing a time.

    Tries various acceptable time formats until one works.

    :param str datestr: A string representing a time taken.
    :returns int: The time taken in minutes.
    """
    patterns = (
        (timeformat1, parse_timeformat1),
        (timeformat2, parse_timeformat2),
        (timeformat3, parse_timeformat3),
        (timeformat4, parse_timeformat4),
    )

    for pattern, parse in patterns:
        if pattern.search(time_string):
            return parse(time_string)

    raise InvalidTimeFormatError(
        "Time format does not match any acceptable formats! " + time_string
    )


def time_spent_on_planner(period, for_date, planner_root):
    """For any date, a time period uniquely maps to a single log file on disk
    for a particular planner instance (which is tied to a wiki root path).
    This function returns the time spent on the planner for the given time
    period and date.

    This is an interface rather than a planner method since it answers a
    question about the historical data tracked at the path managed by the
    planner, rather than the current actionable state of the planner.

    :param :class:`~composer.timeperiod.Period` period: The time period
        for which we want the time spent
    :param :class:`datetime.date` for_date: The date of interest
    :param str planner_root: The root path of the planner wiki
    :returns int: The time spent in minutes.
    """
    if period < Day:
        return 0
    start_date = period.get_start_date(for_date)
    log_path = get_log_filename(start_date, period, planner_root)
    try:
        log = read_file(log_path)
    except FileNotFoundError:
        raise
    try:
        time_spent, _ = read_section(log, 'time spent on planner')
    except ValueError:
        raise LogfileLayoutError(
            "Error: No 'TIME SPENT ON PLANNER' section found in your {period} "
            "log file!".format(period=period)
        )
    time_spent = string_to_time(time_spent.read())

    return time_spent


def get_constituent_logs(period, for_date, planner_root):
    """Get logfiles for the smaller time period constituting the specified
    time period, e.g. all of the day logfiles for the week.

    :param :class:`~composer.timeperiod.Period` period: The time period
        for which we want constituent log files
    :param :class:`datetime.date` for_date: The date of interest
    :param str planner_root: The root path of the planner wiki
    :returns list: The constituent logs
    """
    if period <= Day:
        return []
    start_date = period.get_start_date(for_date)
    end_date = period.get_end_date(for_date)
    constituent_period = get_next_period(period, decreasing=True)
    logs = []
    current_date = start_date
    constituent_end_date = constituent_period.get_end_date(current_date)
    while constituent_end_date <= end_date:
        try:
            log = get_log_for_date(
                constituent_period, current_date, planner_root
            )
        except FileNotFoundError:
            # could be an in-progress period, i.e. no log yet exists
            # or just a missing log. we just skip over it and continue until we
            # hit the end date of the higher period to be sure
            pass
        else:
            logs.append(log)
        current_date = constituent_end_date + timedelta(days=1)
        constituent_end_date = constituent_period.get_end_date(current_date)
    return logs


def ensure_file_does_not_exist(filename, period):
    """Ensure that a file does not already exist on disk. Raises an
    exception if it does.

    :param str filename: The path to the file
    :param :class:`~composer.timeperiod.Period` period: The time period
        for which we are interested in writing a log file
    """
    if os.path.isfile(filename):
        raise LogfileAlreadyExistsError(
            "New {period} logfile already exists!".format(period=period)
        )
