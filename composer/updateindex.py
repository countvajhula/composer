#!/usr/bin/env python
import os

import click

# TODO: need to improve this script to do regex matching on wiki page names,
# and sort the pages by type and in chronological order + Misc/uncategorized

INDEXFILE = "Pages.wiki"
INDEXTITLE = "= INDEX ="


def get_wiki_pages_among_files(fileslist):
    # wikipages = filter(lambda(thisfile): thisfile[-5:]=='.wiki', fileslist)
    return [
        thisfile[:-5] for thisfile in fileslist if thisfile[-5:] == ".wiki"
    ]


def update_index(plannerpath, indexfile=None, indextitle=None):
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
    print()
    print(">>> Operating on wiki at location: %s <<<" % wikipath)
    print()

    update_index(wikipath, file, title)
