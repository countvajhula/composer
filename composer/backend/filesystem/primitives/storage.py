import os

from ....timeperiod import Day, Week, Month, Quarter, Year, quarter_for_month

PATH_SPECIFICATION = "{prefix}/{filename}"
FILENAME_TEMPLATE = {
    Day: "{month} {date}, {year}.wiki",
    Week: "Week of {month} {date}, {year}.wiki",
    Month: "Month of {month}, {year}.wiki",
    Quarter: "{quarter} {year}.wiki",
    Year: "{year}.wiki",
}


def get_log_filename(for_date, period, root=None):
    """Construct a standard filename for a log based on the provided date and
    time period. This is simply a utility to generate a filename from the date
    based on a template for the time period, and is not aware of the actual
    period boundaries that would be used by the planner in creating new files.

    :param :class:`datetime.date` for_date: The date for which to generate
        a filename
    :param :class:`~composer.timeperiod.Period` period: The time period for
        which to determine a filename
    :param str root: The base filesystem path relative to which the path
        should be computed. If no root path is provided, then return just
        the filename
    """
    # compute a filename based on the reference date
    (date, month, year) = (for_date.day, for_date.month, for_date.year)
    quarter = quarter_for_month(month)
    month_name = for_date.strftime("%B")
    filename = FILENAME_TEMPLATE[period].format(
        month=month_name, date=date, quarter=quarter, year=year
    )
    if root:
        path = full_file_path(filename, root=root)
    else:
        path = filename

    return path


def full_file_path(filename, root, dereference=False):
    """Given a path root and a filename, construct an OS-specific filesystem
    path.

    :param str filename: The name of the file
    :param str root: The base path
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
    path = PATH_SPECIFICATION.format(prefix=root, filename=filename)
    return path_fn(path)


def strip_extension(filename):
    """Strip the extension from the end of the filename.

    :param str filename: The filename
    :returns str: The filename sans extension
    """
    index = filename.rfind(".")
    return filename[:index] if index >= 0 else filename


def strip_prefix(filename):
    """Strip the path prefix from the start of the filename.

    :param str filename: The filename
    :returns str: The filename sans path prefix
    """
    # TODO: tests and edge cases
    return filename[filename.rfind("/") + 1 :]


def bare_filename(filename):
    """Strip path prefix as well as extension from a filename.

    :param str filename: The filename
    :returns str: The filename sans path prefix and extension
    """
    return strip_extension(strip_prefix(filename))


def read_file(path):
    """Read a file on disk.

    :param str path: Filesystem path to the file
    :returns str: Contents of the file
    """
    with open(path, "r") as f:
        contents = f.read()
    return contents


def write_file(contents, path):
    """Write a file to disk (overwrites existing file if present).

    :param str contents: Contents to be written to the file
    :param str path: Filesystem path to the file
    """
    with open(path, "w") as f:
        f.write(contents)
