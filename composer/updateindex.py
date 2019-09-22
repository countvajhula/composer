#!/usr/bin/env python
import os

import click

from composer.utils import display_message
from composer.backend.filesystem.primitives import strip_extension

# TODO: need to improve this script to do regex matching on wiki page names,
# and sort the pages by type and in chronological order + Misc/uncategorized

INDEXFILE = "Pages.wiki"
INDEXTITLE = "= INDEX ="


def is_wiki(filename):
    return filename[-5:] == ".wiki"


def get_wiki_pages_among_files(fileslist):
    """ Identify files in the given list that are wiki files, and return these
    sans the .wiki extension.

    :param list fileslist: A list of filenames
    :returns list: Only the wiki files, with extensions truncated
    """
    return map(strip_extension, filter(is_wiki, fileslist))


def update_index(plannerpath, indexfile=None, indextitle=None):
    """ Generate the index from all .wiki files present at the provided
    path. Use the provided filename and title string, if any, or use defaults.
    This generates the index from scratch and overwrites any existing index
    file that may be present.

    :param str plannerpath: The location of the wiki
    :param str indexfile: The filename to use when saving the generated index
    :param str indextitle: A title string to use at the top of the file
    """
    if not indexfile:
        indexfile = INDEXFILE
    if not indextitle:
        indextitle = INDEXTITLE
    fileslist = os.listdir(plannerpath)
    wikipages = get_wiki_pages_among_files(fileslist)
    # print "%d wiki pages found: %s" % (len(wikipages), str(wikipages))
    indexfilename = "%s/%s" % (plannerpath, indexfile)
    wikiindex = open(indexfilename, "w")
    wikiindex.write(indextitle + "\n")
    for page in wikipages:
        wikiindex.write("\t* [[" + page + "]]\n")
    wikiindex.close()


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
    "--file",
    help=("Filename to use for the index (default '{}').".format(INDEXFILE)),
)
@click.option(
    "-t",
    "--title",
    help=("Title for the index page (default '{}')".format(INDEXTITLE)),
)
def main(wikipath, file=None, title=None):
    wikipath = wikipath.rstrip("/")
    display_message()
    display_message(">>> Operating on wiki at location: %s <<<" % wikipath)
    display_message()

    update_index(wikipath, file, title)
