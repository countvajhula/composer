import re

from .files import make_file

SECTION_PATTERN = re.compile(r"^[A-Z][A-Z][A-Za-z ]+:")
SECTION_OR_EOF_PATTERN = re.compile(r"(^[A-Z][A-Z][A-Za-z ]+:|\A\Z)")
TASK_PATTERN = re.compile(r"^\t*\[")
SECTION_SEPARATOR = '\n'


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


is_section_separator = is_blank_line


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
