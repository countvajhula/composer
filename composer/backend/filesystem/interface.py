from .primitives import get_log_filename, read_file


def get_log_for_date(period, for_date, planner_root):
    """ Get the logfile for the specified period that is tracking the
    specified date for the planner at the specified location.

    This is an interface rather than a planner method since it answers a
    question about the historical data tracked at the path managed by the
    planner, rather than the current actionable state of the planner.
    """
    start_date = period.get_start_date(for_date)
    log_path = get_log_filename(start_date, period, planner_root)
    log = read_file(log_path)
    return log
