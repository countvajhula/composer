import re

from .files import make_file

# TODO: probably best to enforce section names as all caps to avoid
# parsing ambiguity with arbitrary non-task entries
SECTION_PATTERN = re.compile(r"^[A-Z][A-Z][A-Za-z ]+:")
SECTION_OR_EOF_PATTERN = re.compile(r"(^[A-Z][A-Z][A-Za-z ]+:|\A\Z)")
TASK_PATTERN = re.compile(r"^\t*\[")
SECTION_SEPARATOR = '\n'


def get_section_pattern(section):
    return re.compile(r'^' + section.upper())


# TODO: replace these type predicates with regexes?
# one advantage is that they would be amenable to pattern-based
# substitutions via re.sub, which could be used for automatic
# processing of tasks in terms of their status
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


is_section_separator = is_blank_line


def is_done_task(line):
    return line.startswith("[x")


def is_invalid_task(line):
    return line.startswith("[-")


def is_undone_task(line):
    return line.startswith("[ ")


def is_wip_task(line):
    return line.startswith("[\\")


def is_eof(line):
    return line == ""


def is_completed(entry):
    """ A predicate function that is true if an entry is 'complete'.

    Note that is_completed and is_unfinished assert opposite cases, but are not
    exhaustive, since there are entries for which completeness is not
    applicable.
    """
    return any(
        (
            is_done_task(entry),
            is_invalid_task(entry),
            is_scheduled_task(entry),  # handled elsewhere
        )
    )


def is_not_completed(entry):
    """ A predicate function that is true if an entry is not 'complete'. This
    additionally excludes blank lines.
    """
    return not is_completed(entry) and not is_blank_line(entry)


def is_unfinished(entry):
    """ A predicate function that is true if an entry is 'incomplete'.

    Note that is_completed and is_unfinished assert opposite cases, but are not
    exhaustive, since there are entries for which completeness is not
    applicable.
    """
    return is_task(entry) and not is_completed(entry)


def parse_task(task):
    """ Parse a task (in string form) into the header (first line) and contents
    (any subtasks or other contents). Useful when we need to parse the header
    independently, e.g. to check for scheduled date and ensure that it's
    present in the header specifically, and not just anywhere in the task.

    :param str task: The task to parse
    :returns tuple: The header and the contents, both strings
    """
    f = make_file(task)
    header = f.readline()
    contents = f.read()
    return header, contents
