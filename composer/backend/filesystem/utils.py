import re

SECTION_HEADER_PATTERN = re.compile(r'^[A-Z][A-Z][A-Za-z ]+:')
TASK_PATTERN = re.compile('^\t*\[')


def quarter_for_month(month):
    if month.lower() in ('january', 'february', 'march'):
        return "Q1"
    elif month.lower() in ('april', 'may', 'june'):
        return "Q2"
    elif month.lower() in ('july', 'august', 'september'):
        return "Q3"
    elif month.lower() in ('october', 'november', 'december'):
        return "Q4"


def read_file(filepath):
    with open(filepath, 'r') as f:
        contents = f.read()
    return contents


def write_file(contents, filepath):
    with open(filepath, 'w') as f:
        f.write(contents)
