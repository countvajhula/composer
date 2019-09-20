from .files import make_file, contain_file_mutation, copy_file
from .parsing import (
    is_section_separator,
    get_section_pattern,
    SECTION_OR_EOF_PATTERN,
    SECTION_SEPARATOR,
    is_eof,
    is_subtask,
)


# This module roughly contains the abstraction level between core planner logic
# and the underlying (filesystem) representation. It roughly deals in "entries"
# and lists of entries, which themselves may be moved between sections in a
# logfile. It should ideally facilitate a separation point where higher-level
# code does not deal in files anymore but rather in entries or sections or
# whatever other high-level abstractions make sense for the planner. This
# separation isn't quite achieved at the moment, and so abstractions do
# currently leak between the layers


def entries_to_string(entries):
    """ Convert a list of entries to a string.
    """
    return "".join(entries)


def string_to_entries(string):
    entries, _ = get_entries(make_file(string))
    return entries


def filter_entries(entries, filter_fn):
    """ Filter a list of entries to only those that satisfy a given filter
    function.
    """
    return [entry for entry in entries if filter_fn(entry)]


def exclude_entries(entries, filter_fn):
    """ Filter a list of entries to only those that do NOT satisfy a given
    filter function.
    """
    return [entry for entry in entries if not filter_fn(entry)]


def partition_entries(entries, filter_fn):
    """ Partition a list of entries into two lists based on some filter
    predicate.  The first list will contain the elements that satisfy the
    predicate, while the second list will contain those that don't.
    """
    filtered = filter_entries(entries, filter_fn)
    excluded = exclude_entries(entries, filter_fn)
    return filtered, excluded


@contain_file_mutation
def read_entry(file):
    """ An 'entry' is any line that begins at the 0th position of the line.
    This could be a blank line, a task, a normal text string, a section
    header, pretty much anything EXCEPT things that begin with a tab
    character, as these are treated as subsidiary entries to be included in
    the parent.

    :param :class:`io.StringIO` file: The file to read from

    :returns str: An entry read from the file
    """
    entry = ""
    complement = make_file()
    line = file.readline()
    if is_eof(line):
        complement = make_file(file.getvalue())
        return None, complement
    entry += line
    line = file.readline()
    while is_subtask(line):
        entry += line
        line = file.readline()
    complement.write(line)
    complement.write(file.read())
    return entry, complement


def _read_entries(file):
    entries = []
    entry, complement = read_entry(file)
    while entry:
        entries.append(entry)
        entry, complement = read_entry(complement)
    return entries


@contain_file_mutation
def get_entries(file, of_type=None):
    """ Parse a given file into entries, based on the supplied criteria.
    An entry generally corresponds to a line in the input file, along with
    any subtask entries that fall under it.

    :param :class:`io.StringIO` file: The file to read from
    :param :class:`_sre.SRE_Pattern` until_pattern: A pattern to look for.
        When this pattern is encountered, parsing stops.
    :param bool or_eof: If reading until the end of the file (without
        the pattern having been encountered) is acceptable
    :param bool inclusive: Whether to include the line at the stopping
        point, i.e. the one containing the pattern.
    :param int starting_position: Buffer position to start reading the
        input file from.
    :param function of_type: Get only entries that match this type. This
        argument should be a predicate function that returns true or
        false based on a type determination on the argument.
    """
    if not of_type:
        of_type = lambda x: True
    entries = [entry for entry in _read_entries(file) if of_type(entry)]
    return entries


@contain_file_mutation
def partition_at(file, pattern, or_eof=False, inclusive=False):
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

    if contents.getvalue():
        # if there is a blank line at the end of the section, treat it
        # as a section separator and don't include it in the secion.
        # Note: This should eventually be unnecessary if we introduce
        # higher-level abstractions with different low-level
        # (e.g. file-based) representations, such that the entities
        # are reasoned about at different levels and their file
        # representation is modulated as a side-effect in a
        # deterministic ("monadic") way
        lines = contents.readlines()
        penultimate_line = lines[-1]
        if is_section_separator(penultimate_line):
            complement.write(penultimate_line)
            contents = make_file("".join(lines[:-1]))
    complement.write(after.read())
    return contents, complement


@contain_file_mutation
def add_to_section(file, section, tasks, above=True, ensure_separator=False):
    """ Find a given section in a file and insert tasks into it.  The new tasks
    can be added either at the top or bottom of the section, and any
    pre-existing contents of the section are preserved alongside the new
    additions.
    """

    try:
        contents, complement = read_section(file, section)
    except ValueError:
        raise
    if not contents.getvalue():
        # "base case"
        pattern = get_section_pattern(section)
        try:
            before, remaining = partition_at(file, pattern, inclusive=True)
        except ValueError:
            raise
        new_file = make_file()
        new_file.write(before.read())
        new_file.write(tasks)
        if (
            ensure_separator
            and not is_section_separator(make_file(tasks).readlines()[-1])
            and remaining.getvalue()
            and not is_section_separator(copy_file(remaining).readlines()[0])
        ):
            # in extracting the section from the original file, we disregarded
            # a section separator (if present). Add it back here. (ideally this
            # level of management should be made unnecessary with higher-level
            # abstractions)
            new_file.write(SECTION_SEPARATOR)
        new_file.write(remaining.read())
        return new_file
    else:
        new_contents = make_file()
        if above:
            new_contents.write(tasks)
            new_contents.write(contents.read())
        else:
            new_contents.write(contents.read())
            new_contents.write(tasks)
        return add_to_section(
            complement,
            section,
            new_contents.getvalue(),
            above,
            ensure_separator,
        )
