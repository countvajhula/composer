#!/usr/bin/env python
import os
import platform

import click

from collections import namedtuple
from functools import partial

from composer.utils import display_message
from composer.backend.filesystem.primitives import bare_filename

# TODO: need to improve this script to do regex matching on wiki page names,
# and sort the pages by type and in chronological order + Misc/uncategorized

INDEX_FILE_PREFIX = "pages"
INDEX_TITLE = "index"

PreIndex = namedtuple('Index', 'name sort sort_order')
Index = namedtuple('Index', 'name title entries filename')


def is_wiki(filename):
    return filename[-5:] == ".wiki"


def get_files(path, of_type=None):
    """ Get all files at the specified path of the specified type.

    :param str path: The location of the wiki
    :returns list: Only the wiki files, with extensions truncated
    """
    files = os.listdir(path)
    if of_type:
        files = filter(of_type, files)
    files = [os.path.join(path, f) for f in files]
    return files


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def write_index(path_to_file, title, entries):
    """ Write an index file at the given path, with the given title and
    contents.

    :param str path_to_file: The path to the index file
    :param str title: A title string to use at the top of the file
    :param list entries: A list of entries to be written as the contents
        of the index file.
    """
    with open(path_to_file, "w") as f:
        f.write(title + "\n")
        for page in entries:
            f.write(page)


def identity(x):
    return x


def wikify(entry, prefix=None):
    if prefix:
        return "\t* [[{prefix}_{name}|{name}]]\n".format(
            prefix=prefix, name=entry
        )
    else:
        return "\t* [[{name}]]\n".format(name=entry)


def format_for_display(pages):
    """ Format a representation of a list of wiki pages into a readable
    form for display in the index.

    :param list pages: The list of wiki filenames
    :retutns list: The list of wiki pages
    """
    filenames = map(wikify, map(bare_filename, pages))
    return filenames


def prepare_root_index(contents, path, file_prefix, title):
    """ Prepare the root wiki index page linking to the provided contents

    :param list contents: A list containing the names (str) of the sorted
        indexes.
    :param str path: The path to the location where the index is to be saved
    :param str file_prefix: The filename prefix to use for the index files.
        It will be used as the actual filename of the root index.
    :param str title: The title for the index page

    :returns Index: The prepared index
    """
    filename = os.path.join(path, "{}.wiki".format(file_prefix.capitalize()))
    title = "= {} =".format(title).upper()
    prefix = file_prefix.capitalize()
    _wikify = partial(wikify, prefix=prefix)
    entries = map(_wikify, contents)
    return Index('root', title, entries, filename)


def prepare_index(contents, path, file_prefix, root_title, preindex):
    """ Prepare a wiki index page for the provided contents, with the specified
    properties.

    :param list contents: A list containing the filenames (str) to be included
        in the index.
    :param str path: The path to the location where the index is to be saved
    :param str file_prefix: The filename prefix to use for the index file.
    :param str root_title: The title used for the root index page

    :returns Index: The prepared index
    """
    index_name, sort_fn, is_reversed = preindex
    entries = format_for_display(
        sorted(contents, key=sort_fn, reverse=is_reversed)
    )
    title = "= {} ({}) =".format(root_title, index_name).upper()

    filename = os.path.join(
        path,
        "{prefix}_{name}.wiki".format(
            prefix=file_prefix.capitalize(), name=index_name.capitalize()
        ),
    )
    return Index(index_name, title, entries, filename)


def update_index(path, filename=None, title=None):
    """ Generate the index from all .wiki files present at the provided
    path. Use the provided filename and title string, if any, or use defaults.
    This generates the index from scratch and overwrites any existing index
    files that may be present. It generates a root index linking to actual
    index files, each of which are sorted according to different criteria.

    :param str path: The location of the wiki
    :param str filename: The filename (not including extension) to use when
        saving the generated index
    :param str title: A title string to use at the top of the file
    """
    if not filename:
        file_prefix = INDEX_FILE_PREFIX
    if not title:
        title = INDEX_TITLE
    files = get_files(path, is_wiki)

    preindexes = [
        PreIndex('alphabetical', identity, False),
        PreIndex('by date modified', os.path.getmtime, True),
        PreIndex('by date created', creation_date, True),
    ]

    # prepare the individual indexes according to whatever sorting order
    prepare = partial(prepare_index, files, path, file_prefix, title)
    indexes = list(map(prepare, preindexes))

    # prepare main index file
    index_names = [i.name.capitalize() for i in indexes]
    root_index = prepare_root_index(index_names, path, file_prefix, title)
    indexes.append(root_index)

    # write all of the index files
    for _, title, entries, filename in indexes:
        write_index(filename, title, entries)


@click.command(
    help=(
        'Regenerate the index for the wiki at the indicated path. '
        'This will result in any newly created pages being included in '
        'the index.\n'
    )
)
@click.argument("wikipath")
@click.option(
    "-f",
    "--filename",
    help=(
        "Filename to use for the index (default '{}').".format(
            INDEX_FILE_PREFIX
        )
    ),
)
@click.option(
    "-t",
    "--title",
    help=("Title for the index page (default '{}')".format(INDEX_TITLE)),
)
def main(wikipath, filename=None, title=None):
    wikipath = wikipath.rstrip("/")
    display_message()
    display_message(">>> Operating on wiki at location: %s <<<" % wikipath)
    display_message()

    update_index(wikipath, filename, title)
