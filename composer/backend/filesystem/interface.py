from datetime import timedelta
from ...timeperiod import get_next_period, Day
from .primitives import get_log_filename, read_file


def get_log_for_date(period, for_date, planner_root):
    """ Get the logfile for the specified period that is tracking the
    specified date for the planner at the specified location.

    This is an interface rather than a planner method since it answers a
    question about the historical data tracked at the path managed by the
    planner, rather than the current actionable state of the planner.
    """
    if period < Day:
        return None
    start_date = period.get_start_date(for_date)
    log_path = get_log_filename(start_date, period, planner_root)
    log = read_file(log_path)
    return log


def get_constituent_logs(period, for_date, planner_root):
    """ Get logfiles for the smaller time period constituting the specified
    time period, e.g. all of the day logfiles for the week.
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
            log = get_log_for_date(constituent_period, current_date, planner_root)
        except FileNotFoundError:
            # in-progress period, i.e. no log yet exists
            break
        logs.append(log)
        current_date = constituent_end_date + timedelta(days=1)
        constituent_end_date = constituent_period.get_end_date(current_date)
    return logs
