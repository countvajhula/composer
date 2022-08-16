import re

# TODO: change these to annotated regex's

# N mins
_timeformat1 = re.compile(r"(\d+) ?mins?", re.IGNORECASE)
# H hrs M mins
_timeformat2 = re.compile(r"(\d+) ?hrs? ?(\d+) ?mins?", re.IGNORECASE)
timeformat1 = re.compile(r"^" + _timeformat1.pattern + r"$", re.IGNORECASE)
timeformat2 = re.compile(r"^" + _timeformat2.pattern + r"$", re.IGNORECASE)
timeformat3_prefix = re.compile(r"^\d+ ?\+ ?\d+ ?= ?", re.IGNORECASE)
valid_formats_3 = [_timeformat1, _timeformat2]
# X + Y = Z
_timeformat3 = [
    re.compile(timeformat3_prefix.pattern + x.pattern) for x in valid_formats_3
]
timeformat3 = re.compile(r'|'.join(fmt.pattern + r'$' for fmt in _timeformat3))
valid_formats_4 = [_timeformat1, _timeformat2] + _timeformat3
timeformat4_suffix = re.compile(r' ?\(.*\)')
# T (completed next day)
timeformat4 = re.compile(
    r'|'.join(x.pattern + timeformat4_suffix.pattern for x in valid_formats_4)
)


def parse_timeformat1(time_string):
    """Parse time format
        N mins (with optional space and optional s)
    :param str time_string: The string representation of the time
    :returns int: The parsed time, in minutes.
    """
    time = timeformat1.search(time_string).groups()
    mins = int(time[0])
    return mins


def parse_timeformat2(time_string):
    """Parse time format
        H hrs N mins (with optional space and optional s's)
    :param str time_string: The string representation of the time
    :returns int: The parsed time, in minutes.
    """
    time = timeformat2.search(time_string).groups()
    hr, min = time
    mins = int(hr) * 60 + int(min)

    return mins


def parse_timeformat3(time_string):
    """Parse time format 3 (see above).

    :param str time_string: The string representation of the time
    :returns int: The parsed time, in minutes.
    """
    time = timeformat3.search(time_string).groups()
    a, b, c = time
    if a:
        mins = int(a)
    else:
        mins = int(b) * 60 + int(c)

    return mins


def parse_timeformat4(time_string):
    """Parse time format 4 (see above).

    :param str time_string: The string representation of the time
    :returns int: The parsed time, in minutes.
    """
    time = timeformat4.search(time_string).groups()
    a, b, c, d, e, f = time
    if a:
        mins = int(a)
    elif b:
        mins = int(b) * 60 + int(c)
    elif d:
        mins = int(d)
    elif e:
        mins = int(e) * 60 + int(f)

    return mins
