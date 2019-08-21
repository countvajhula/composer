import re

from functools import wraps

SECTION_PATTERN = re.compile(r"^[A-Z][A-Z][A-Za-z ]+:")
SECTION_OR_EOF_PATTERN = re.compile(r"(^[A-Z][A-Z][A-Za-z ]+:|\A\Z)")
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
        new_kwargs = {k: (copy_file(v) if isinstance(v, StringIO) else v) for k, v in kwargs.items()}
        result = fn(*new_args, **new_kwargs)
        if isinstance(result, tuple):
            new_result = [copy_file(r) if isinstance(r, StringIO) else r for r in result]
        else:
            new_result = copy_file(result) if isinstance(result, StringIO) else result
        return new_result
    return wrapper


def quarter_for_month(month):
    if month.lower() in ("january", "february", "march"):
        return "Q1"
    elif month.lower() in ("april", "may", "june"):
        return "Q2"
    elif month.lower() in ("july", "august", "september"):
        return "Q3"
    elif month.lower() in ("october", "november", "december"):
        return "Q4"


def get_section_pattern(section):
    return re.compile(r'^' + section.upper())


# TODO: replace these type predicates with regexes?
def is_scheduled_task(line):
    return line.startswith("[o")


def is_task(line):
    return line.startswith("[")


def is_subtask(line):
    return line.startswith("\t")


def is_section(line, section_name=None):
    pattern = (
        get_section_pattern(section_name) if section_name else SECTION_PATTERN
    )
    return pattern.search(line)


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


def item_list_to_string(items):
    return "".join(items)


def string_to_item_list(string):
    items, _ = get_task_items(make_file(string))
    return items


@contain_file_mutation
def read_item(file, of_type=None, starting_position=0):
    """ An 'item' is any line that begins at the 0th position of the line.
    This could be a blank line, a task, a normal text string, a section
    header, pretty much anything EXCEPT things that begin with a tab
    character, as these are treated as subsidiary items to be included in
    the parent.

    :param :class:`io.StringIO` file: The file to read from
    :param function of_type: A predicate function that returns true or
        false based on a type determination on the argument
    :param int starting_position: Buffer position to start reading the
        input file from.

    :returns str: An item read from the file
    """
    if not of_type:
        of_type = lambda x: True
    item = ""
    complement = make_file()
    index = file.seek(starting_position)
    line = file.readline()
    while not is_eof(line) and not of_type(line):
        complement.write(line)
        line = file.readline()
    if is_eof(line):
        return None, -1, complement  # -1 OK?
    item += line
    index = file.tell()
    line = file.readline()
    while is_subtask(line):
        item += line
        index = file.tell()
        line = file.readline()
    complement.write(line)
    complement.write(file.read())
    return item, index, complement


@contain_file_mutation
def read_until(
    file, pattern, or_eof=False, inclusive=False, starting_position=0
):
    """ Read a given file until a string matching a certain pattern
    is encountered.

    :param :class:`io.StringIO` file: The file to read from
    :param :class:`_sre.SRE_Pattern` pattern: The pattern to look for
    :param bool or_eof: If reading until the end of the file (without
        the pattern having been encountered) is acceptable
    :param bool inclusive: Whether to include the line at the stopping
        point, i.e. the one containing the pattern.
    :param int starting_position: Buffer position to start reading the
        input file from.
    """
    contents = ""
    complement = make_file()
    complement.write(file.read(starting_position))
    index = file.tell()
    item, next_index, _ = read_item(file, starting_position=index)
    while item and not pattern.search(item):
        contents += item
        index = next_index
        item, next_index, _ = read_item(file, starting_position=index)
    if item and pattern.search(item):
        if inclusive:
            contents += item
            index = next_index
        else:
            complement.write(item)
        file.seek(next_index)
        complement.write(file.read())
    else:
        if not or_eof:
            raise ValueError("Pattern {} not found in file!".format(pattern))
    return contents, index, complement


@contain_file_mutation
def read_section(file, section):
    pattern = get_section_pattern(section)
    complement = make_file()
    try:
        contents_before, index, _ = read_until(file, pattern, inclusive=True)
        complement.write(contents_before)
        contents, index, _ = read_until(
            file, SECTION_OR_EOF_PATTERN, or_eof=True, starting_position=index
        )
    except ValueError:
        raise

    file.seek(index)
    contents_after = file.read()
    complement.write(contents_after)
    return contents, index, complement


@contain_file_mutation
def add_to_section(file, section, tasks):
    """ Find a given section in a file and insert tasks into it.
    The new tasks added at the top of the section, and any pre-existing
    contents of the section are preserved below the new additions.
    """
    pattern = get_section_pattern(section)
    try:
        contents, index, _ = read_until(file, pattern, inclusive=True)
    except ValueError:
        raise
    new_file = make_file(contents)
    new_file.read()
    new_file.write(tasks)
    file.seek(index)
    rest_of_file = file.read()
    new_file.write(rest_of_file)
    return new_file


@contain_file_mutation
def get_task_items(file, of_type=None):
    tasks = []
    complement = make_file()
    item, _, complement = read_item(file, of_type)
    while item:
        tasks.append(item)
        item, _, complement = read_item(complement, of_type)
    return tasks, complement


def make_file(string=""):
    """ 'Files' are the abstraction level at which the planner is implemented
    in terms of the filesystem. We prefer to work with files rather than the
    more elementary string representation.
    """
    return StringIO(string)


def copy_file(file):
    # we only operate on StringIO files and not actual files
    # except at the entry and exit points
    return make_file(file.getvalue())


def read_file(filepath):
    with open(filepath, "r") as f:
        contents = f.read()
    return contents


def write_file(contents, filepath):
    with open(filepath, "w") as f:
        f.write(contents)
