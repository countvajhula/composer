import re

# TODO: change these to annotated regex's

# N mins
_timeformat_min = r"(\d+) ?mins?"
# H hrs
_timeformat_hr = r"(\d+) ?hrs?"
# H hrs M mins
_timeformat_hrmin = r"(\d+) ?hrs? ?(\d+) ?mins?"
timeformat_min = re.compile(r"^" + _timeformat_min + r"$", re.IGNORECASE)
timeformat_hr = re.compile(r"^" + _timeformat_hr + r"$", re.IGNORECASE)
timeformat_hrmin = re.compile(r"^" + _timeformat_hrmin + r"$", re.IGNORECASE)
_timeformat_breakdown_prefix = r"^\d.*\+ ?\d.*= ?"
valid_base_formats = [_timeformat_min, _timeformat_hr, _timeformat_hrmin]
# X + Y = Z
_timeformat_pfx = [
    _timeformat_breakdown_prefix + x for x in valid_base_formats
]
timeformat_pfx = re.compile(r'|'.join(fmt + r'$' for fmt in _timeformat_pfx))
valid_base_formats = valid_base_formats + _timeformat_pfx
_timeformat_annotation_suffix = r' ?\(.*\)'
# T (completed next day)
timeformat_sfx = re.compile(
    r'|'.join(x + _timeformat_annotation_suffix for x in valid_base_formats)
)


def parse_timeformat_min(time_string):
    """Parse time format
        N mins (with optional space and optional s)
    :param str time_string: The string representation of the time
    :returns int: The parsed time, in minutes.
    """
    time = timeformat_min.search(time_string).groups()
    mins = int(time[0])
    return mins


def parse_timeformat_hr(time_string):
    """Parse time format
        N hrs (with optional space and optional s)
    :param str time_string: The string representation of the time
    :returns int: The parsed time, in minutes.
    """
    time = timeformat_hr.search(time_string).groups()
    mins = int(time[0]) * 60
    return mins


def parse_timeformat_hrmin(time_string):
    """Parse time format
        H hrs N mins (with optional space and optional s's)
    :param str time_string: The string representation of the time
    :returns int: The parsed time, in minutes.
    """
    time = timeformat_hrmin.search(time_string).groups()
    hr, min = time
    mins = int(hr) * 60 + int(min)

    return mins


def parse_timeformat_pfx(time_string):
    """Parse time format 3 (see above).

    :param str time_string: The string representation of the time
    :returns int: The parsed time, in minutes.
    """
    time = timeformat_pfx.search(time_string).groups()
    a, b, c1, c2 = time
    if a:
        mins = int(a)
    elif b:
        mins = int(b) * 60
    else:
        mins = int(c1) * 60 + int(c2)

    return mins


def parse_timeformat_sfx(time_string):
    """Parse time format 4 (see above).

    :param str time_string: The string representation of the time
    :returns int: The parsed time, in minutes.
    """
    time = timeformat_sfx.search(time_string).groups()
    a, b, c1, c2, d, e, f1, f2 = time
    if a:
        mins = int(a)
    elif b:
        mins = int(b) * 60
    elif c1:
        mins = int(c1) * 60 + int(c2)
    elif d:
        mins = int(d)
    elif e:
        mins = int(e) * 60
    elif f1:
        mins = int(f1) * 60 + int(f2)

    return mins
