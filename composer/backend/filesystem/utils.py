import re

from functools import wraps

SECTION_PATTERN = re.compile(r"^[A-Z][A-Z][A-Za-z ]+:")
SECTION_OR_EOF_PATTERN = re.compile(r"(^[A-Z][A-Z][A-Za-z ]+:|^$)")
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


def is_eof(line):
    return line == ""


def read_item(file, of_type=None, starting_position=0):
    """ An 'item' is any line that begins at the 0th position of the line.
    This could be a blank line, a task, a normal text string, a section
    header, pretty much anything EXCEPT things that begin with a tab
    character, as these are treated as subsidiary items to be included in
    the parent.
    """
    if not of_type:
        of_type = lambda x: True
    contents = ""
    index = file.seek(starting_position)
    line = file.readline()
    while not is_eof(line) and not of_type(line):
        line = file.readline()
    if is_eof(line):
        return None
    contents += line
    index = file.tell()
    line = file.readline()
    while is_subtask(line):
        contents += line
        index = file.tell()
        line = file.readline()
    return (contents, index
            if contents
            else None)


def read_until(file, pattern, inclusive=False, starting_position=0):
    contents = ""
    index = file.seek(starting_position)
    item, index = read_item(file, starting_position=index)
    while item and not pattern.search(item):
        contents += item
        item, index = read_item(file, starting_position=index)
    if pattern.search(item):
        if inclusive:
            contents += item
            index = file.tell()
    else:
        raise ValueError("Pattern {} not found in file!" .format(pattern))
    return contents, index


def read_section(file, section):
    pattern = re.compile(r'^' + section.upper())
    try:
        _, index = read_until(file, pattern, inclusive=True)
        contents, _ = read_until(file, SECTION_OR_EOF_PATTERN, starting_position=index)
    except ValueError:
        raise
    return contents


@contain_file_mutation
def add_to_section(file, section, tasks):
    pattern = re.compile(r'^' + section.upper())
    _, index = read_until(file, pattern, inclusive=True)
    file.seek(index)
    file.write(tasks)
    return file


def get_tasks(file, section=None, of_type=None):
    tasks = ""
    if section:
        task_file = make_file(read_section(file, section))
    item, index = read_item(task_file, of_type)
    while item:
        tasks += item
        item, index = read_item(task_file, of_type, index)
    return tasks


def make_file(string):
    """ 'Files' are the abstraction level at which the planner is implemented
    in terms of the filesystem. We prefer to work with files rather than the
    more elementary string representation.
    """
    return StringIO(string)


def copy_file(file):
    # we only operate on StringIO files and not actual files
    # except at the entry and exit points
    return StringIO(file.getvalue())


def read_file(filepath):
    with open(filepath, "r") as f:
        contents = f.read()
    return contents


def write_file(contents, filepath):
    with open(filepath, "w") as f:
        f.write(contents)
