from functools import wraps

from .storage import read_file as _read_file
from .storage import write_file as _write_file

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


def contain_file_mutation(fn):
    """For functions that operate on files, this makes is so that these file
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


def make_file(contents=""):
    """'Files' (entailing the concept of "lines") are the abstraction level at
    which the planner is implemented in terms of the filesystem. We prefer to
    work with files rather than the more elementary string representation. On
    the other hand, files also entail the idea of storage and a hierarchical
    namespace. We are concerned with the former notion of a file here, rather
    than the storage and indexing concerns.

    :param str contents: A string to be treated as a file
    :returns :class:`io.StringIO`: A file representation of the input
    """
    return StringIO(contents)


def copy_file(file):
    """Make a logical copy of a file (i.e. at the abstraction level of files
    rather than the filesystem).

    :param :class:`io.StringIO` file: The file to copy
    :returns :class:`io.StringIO`: A copy of the file
    """
    # we only operate on StringIO files and not actual files
    # except at the entry and exit points
    return make_file(file.getvalue())


def read_file(filename):
    """Read a file on disk and produce an in-memory logical representation
    of the file. This logical representation will be used for analysis and
    processing so that the actual file on disk isn't affected until any
    such processing is complete.

    :param filename: Path to a file on disk
    :returns :class:`io.StringIO`: A logical file mirroring the file on disk
    """
    contents = _read_file(filename)
    return make_file(contents)


def write_file(file, filename):
    """Write a logical file as an actual file on disk.

    :param :class:`io.StringIO` file: The file to write
    :param filename: Path to write to
    """
    _write_file(file.read(), filename)


@contain_file_mutation
def partition_at(file, pattern, or_eof=False, inclusive=False):
    """Partition a file into two files at the occurrence of a pattern.  The
    first file will contain the contents before the pattern, while the second
    list will contain those after it.

    :param :class:`io.StringIO` file: A text file to partition
    :param :class:`_sre.SRE_Pattern` pattern: A pattern (regex) to find
    :param bool or_eof: If true, then handles missing pattern gracefully
        and does not treat it as an error. Otherwise, raises an error if the
        pattern is missing.
    :param bool inclusive: Whether to include the pattern in the 'before' file
    :returns tuple: A pair with a file containing the contents before
        the pattern, and another file containing the contents after
    """
    before, after = make_file(), make_file()
    line = file.readline()
    while line:
        if not pattern.search(line):
            before.write(line)
            line = file.readline()
            continue
        if inclusive:
            before.write(line)
        else:
            after.write(line)
        break
    if not line and not or_eof:
        raise ValueError("Pattern {} not found in file!".format(pattern))
    after.write(file.read())

    return before, after


@contain_file_mutation
def append_files(first_file, second_file):
    """Concatenate two files.

    :param first_file: The first file
    :param second_file: The second file
    """
    return make_file(first_file.read() + second_file.read())
