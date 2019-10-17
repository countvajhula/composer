#!/usr/bin/env python
import os

import click

from composer.utils import display_message
from composer.backend.filesystem.primitives import bare_filename

# TODO: need to improve this script to do regex matching on wiki page names,
# and sort the pages by type and in chronological order + Misc/uncategorized

INDEXFILE = "Pages.wiki"
INDEXTITLE = "= INDEX ="


def is_wiki(filename):
    return filename[-5:] == ".wiki"


def get_files(path, of_type=None):
    """ Get all files at the specified path of the specified type.

    :param str plannerpath: The location of the wiki
    :returns list: Only the wiki files, with extensions truncated
    """
    files = os.listdir(path)
    if of_type:
        files = filter(of_type, files)
    files = [os.path.join(path, f) for f in files]
    return files


def sort_files(files):
    return sorted(files)  # alphabetical order


def format_for_display(files):
    return map(bare_filename, files)


def update_index(plannerpath, filename=None, title=None):
    """ Generate the index from all .wiki files present at the provided
    path. Use the provided filename and title string, if any, or use defaults.
    This generates the index from scratch and overwrites any existing index
    file that may be present.

    :param str plannerpath: The location of the wiki
    :param str filename: The filename to use when saving the generated index
    :param str title: A title string to use at the top of the file
    """
    if not filename:
        filename = INDEXFILE
    if not title:
        title = INDEXTITLE
    files = get_files(plannerpath, is_wiki)
    files = sort_files(files)
    files = format_for_display(files)
    # print "%d wiki pages found: %s" % (len(wikipages), str(wikipages))
    index_filename = os.path.join(plannerpath, filename)
    with open(index_filename, "w") as f:
        f.write(title + "\n")
        for page in files:
            f.write("\t* [[" + page + "]]\n")


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
    help=("Filename to use for the index (default '{}').".format(INDEXFILE)),
)
@click.option(
    "-t",
    "--title",
    help=("Title for the index page (default '{}')".format(INDEXTITLE)),
)
def main(wikipath, filename=None, title=None):
    wikipath = wikipath.rstrip("/")
    display_message()
    display_message(">>> Operating on wiki at location: %s <<<" % wikipath)
    display_message()

    update_index(wikipath, filename, title)
