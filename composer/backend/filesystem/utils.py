import re

from functools import wraps

SECTION_PATTERN = re.compile(r"^[A-Z][A-Z][A-Za-z ]+:")
TASK_PATTERN = re.compile(r"^\t*\[")

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


def contain_file_mutation(fn):
    """ For functions that operate on files, this makes is so that these file
    arguments are passed in "by value" rather than "by reference," so that
    any mutation done on the file as part of processing (e.g. even just reading
    the file amounts to this, since it modifies the state of the file viz. its
    "read position") is contained within the function and not reflected in the
    calling context. This allows file processing to be done in a "functional"
    way, keeping side-effects contained and eliminating the need for state
    management.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        new_args = [copy_file(arg) if isinstance(arg, StringIO) else arg for arg in args]
        new_kwargs = dict([(k, copy_file(v)) if isinstance(v, StringIO) else (k, v) for k, v in kwargs.items()])
        return fn(*new_args, **new_kwargs)
    return fn


def quarter_for_month(month):
    if month.lower() in ("january", "february", "march"):
        return "Q1"
    elif month.lower() in ("april", "may", "june"):
        return "Q2"
    elif month.lower() in ("july", "august", "september"):
        return "Q3"
    elif month.lower() in ("october", "november", "december"):
        return "Q4"


def _read_to_section(input_file, section_name=None):
    # if section_name is not specified, reads until the very next section
    # (whatever it may be)
    # return contents from the input file up to but not including
    # the section header if found, and the entire file contents if not
    pattern = (
        re.compile(r'^' + section_name.upper())
        if section_name
        else SECTION_HEADER_PATTERN
    )
    contents = ""
    index = input_file.tell()
    current_line = input_file.readline()
    while current_line != "" and not pattern.search(current_line):
        contents += current_line
        index = input_file.tell()
        current_line = input_file.readline()
    return index, contents


def is_scheduled_task(line):
    return line.startswith("[o")


def is_task(line):
    return line.startswith("[")


def is_subtask(line):
    return line.startswith("\t")


def is_section(section_name, current_line):
    return re.search(r'^' + section_name.upper(), current_line)


def is_blank_line(line):
    return line.startswith("\n")


def is_completed_task(line):
    return line.startswith("[x")


def is_invalid_task(line):
    return line.startswith("[-")


def is_undone_task(line):
    return line.startswith("[ ")


def is_wip_task(line):
    return line.startswith("[\\")


def read_section(input_file, section_name):
    index, _ = _read_to_section(input_file, section_name)
    input_file.seek(index)
    line = input_file.readline()
    if not is_section(section_name, line):
        raise ValueError("Section not found in file!")
    line = input_file.readline()
    _, contents = _read_to_section(input_file)
    return contents


def read_file(filepath):
    with open(filepath, "r") as f:
        contents = f.read()
    return contents


def write_file(contents, filepath):
    with open(filepath, "w") as f:
        f.write(contents)
