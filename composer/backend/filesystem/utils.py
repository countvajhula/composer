import re

SECTION_PATTERN = re.compile(r"^[A-Z][A-Z][A-Za-z ]+:")
TASK_PATTERN = re.compile(r"^\t*\[")


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
