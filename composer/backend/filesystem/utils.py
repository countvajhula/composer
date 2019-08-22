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
        new_args = [
            copy_file(arg) if isinstance(arg, StringIO) else arg
            for arg in args
        ]
        new_kwargs = {
            k: (copy_file(v) if isinstance(v, StringIO) else v)
            for k, v in kwargs.items()
        }
        result = fn(*new_args, **new_kwargs)
        if isinstance(result, tuple):
            new_result = [
                copy_file(r) if isinstance(r, StringIO) else r for r in result
            ]
        else:
            new_result = (
                copy_file(result) if isinstance(result, StringIO) else result
            )
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
def read_item(file):
    """ An 'item' is any line that begins at the 0th position of the line.
    This could be a blank line, a task, a normal text string, a section
    header, pretty much anything EXCEPT things that begin with a tab
    character, as these are treated as subsidiary items to be included in
    the parent.

    :param :class:`io.StringIO` file: The file to read from

    :returns str: An item read from the file
    """
    item = ""
    complement = make_file()
    line = file.readline()
    if is_eof(line):
        complement = make_file(file.getvalue())
        return None, complement
    item += line
    line = file.readline()
    while is_subtask(line):
        item += line
        line = file.readline()
    complement.write(line)
    complement.write(file.read())
    return item, complement


def _read_items(file):
    items = []
    item, complement = read_item(file)
    while item:
        items.append(item)
        item, complement = read_item(complement)
    return items


@contain_file_mutation
def get_task_items(
    file,
    of_type=None,
):
    """ Parse a given file into task items, based on the supplied criteria.
    A task item generally corresponds to a line in the input file, along with
    any subtasks items that fall under it.

    :param :class:`io.StringIO` file: The file to read from
    :param :class:`_sre.SRE_Pattern` until_pattern: A pattern to look for.
        When this pattern is encountered, parsing stops.
    :param bool or_eof: If reading until the end of the file (without
        the pattern having been encountered) is acceptable
    :param bool inclusive: Whether to include the line at the stopping
        point, i.e. the one containing the pattern.
    :param int starting_position: Buffer position to start reading the
        input file from.
    :param function of_type: Get only task items that match this type. This
        argument should be a predicate function that returns true or
        false based on a type determination on the argument.
    """
    if not of_type:
        of_type = lambda x: True
    items = [item for item in _read_items(file) if of_type(item)]
    return items


@contain_file_mutation
def partition_at(
    file, pattern, or_eof=False, inclusive=False,
):
    contents, complement = make_file(), make_file()
    line = file.readline()
    while line:
        if not pattern.search(line):
            contents.write(line)
            line = file.readline()
            continue
        if inclusive:
            contents.write(line)
        else:
            complement.write(line)
        break
    if not line and not or_eof:
        raise ValueError("Pattern {} not found in file!".format(pattern))
    complement.write(file.read())

    return contents, complement


@contain_file_mutation
def read_section(file, section):
    pattern = get_section_pattern(section)
    complement = make_file()
    try:
        before, remaining = partition_at(file, pattern, inclusive=True)
        complement.write(before.read())
        contents, after = partition_at(
            remaining, SECTION_OR_EOF_PATTERN, or_eof=True
        )
    except ValueError:
        raise

    complement.write(after.read())
    return contents, complement


@contain_file_mutation
def add_to_section(file, section, tasks):
    """ Find a given section in a file and insert tasks into it.
    The new tasks added at the top of the section, and any pre-existing
    contents of the section are preserved below the new additions.
    """
    pattern = get_section_pattern(section)
    try:
        before, remaining = partition_at(file, pattern, inclusive=True)
    except ValueError:
        raise
    new_file = make_file()
    new_file.write(before.read())
    new_file.write(tasks)
    new_file.write(remaining.read())
    return new_file


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
