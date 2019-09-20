import os

from ....timeperiod import Day, Week, Month, Quarter, Year

PATH_SPECIFICATION = "{path}/{filename}"
FILENAME_TEMPLATE = {
    Day: "{month} {date}, {year}.wiki",
    Week: "Week of {month} {date}, {year}.wiki",
    Month: "Month of {month}, {year}.wiki",
    Quarter: "{quarter} {year}.wiki",
    Year: "{year}.wiki",
}


def quarter_for_month(month):
    if month.lower() in ("january", "february", "march"):
        return "Q1"
    elif month.lower() in ("april", "may", "june"):
        return "Q2"
    elif month.lower() in ("july", "august", "september"):
        return "Q3"
    elif month.lower() in ("october", "november", "december"):
        return "Q4"


def get_log_filename(for_date, period, root=None):
    """ A time period uniquely maps to a single log file on disk for a
    particular planner instance (which is tied to a wiki root path).  This
    function returns that filename, given a time period. At the moment this
    simply assumes that the reference date is the start of the indicated
    period and constructs a standard filename based on that, but it may be
    desirable to infer the correct filename for the actual or hypothetical
    logfile that would encompass the reference date, based on the current
    period boundary criteria used by the planner.

    :param bool is_existing: Whether to return the filename for an existing
        log file for the indicated period. If true, then this simply uses
        the current state on disk and doesn't compute the filename
    :param :class:`composer.timeperiod.Period` period: The time period for
        which to determine a filename
    :param str root: The base filesystem path relative to which the path
        should be computed. If no root path is provided, then return just
        the filename
    """
    # compute a filename based on the reference date
    (date, month, year) = (
        for_date.day,
        for_date.strftime("%B"),
        for_date.year,
    )
    quarter = quarter_for_month(month)

    filename = FILENAME_TEMPLATE[period].format(
        month=month, date=date, quarter=quarter, year=year
    )
    if root:
        path = full_file_path(root, filename=filename)

    return path


def full_file_path(root, filename, dereference=False):
    """ Given a path root and a filename, construct an OS-specific filesystem
    path.

    :param str root: The base path
    :param str filename: The name of the file
    :param bool dereference: If the file is a symbolic link, the constructed
    path could either return the path to the link, or the path to the linked
    original file. If dereference is True, then return the path to the original
    file, otherwise to the link itself without following it.

    :returns str: The constructed path
    """
    if dereference:
        path_fn = os.path.realpath
    else:
        path_fn = os.path.abspath
    return path_fn(PATH_SPECIFICATION.format(path=root, filename=filename))


def read_file(filepath):
    with open(filepath, "r") as f:
        contents = f.read()
    return contents


def write_file(contents, filepath):
    with open(filepath, "w") as f:
        f.write(contents)
