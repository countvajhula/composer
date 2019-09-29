#!/usr/bin/env python

import os
import re

import click

from random import choice

from . import config
from .utils import display_message

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO

CONFIG_ROOT = os.getenv("COMPOSER_ROOT", os.path.expanduser("~/.composer"))
CONFIG_FILE = os.path.join(CONFIG_ROOT, config.CONFIG_FILENAME)


def extract_lessons(lessons_files):
    """ Extract lessons from the provided files.

    Note that lines beginning with a number are treated as lessons, and
    everything else is ignored.

    :param list lessons_files: List of files (FLOs) from which to extract
        lessons
    :returns list: A list containing all lessons in a file with leading
        numbering removed and a single trailing \n added
    """

    def extract_lessons_raw(f):
        line = f.readline()
        if not line:
            return []
        line_fmt = re.sub(r"^\d+[a-z]?[A-Z]?\. ?", "", line)
        if len(line_fmt) <= 1 or line_fmt == line:
            return extract_lessons_raw(f)
        line_fmt = line_fmt.rstrip("\n") + "\n"
        return [line_fmt] + extract_lessons_raw(f)

    # combine all lessons from different files into one list
    lessons = map(extract_lessons_raw, lessons_files)
    lessons = [item for sublist in lessons for item in sublist]  # flatten
    return lessons


def get_advice(lessons_files):
    """ Extract individual lessons from files into a flat list.

    :param list lessons_files: List of files (FLOs) from which to extract
        lessons
    """
    lessons = extract_lessons(lessons_files)
    # return lesson by choosing a random element of this list
    if lessons:
        return choice(lessons)
    return ""


@click.command(
    help=(
        "Select and display a random piece of advice from the configured "
        "advice files.\n"
        "WIKIPATH is the path of the wiki to operate on.\n"
        "If not provided, uses the path(s) specified in "
        "config.ini"
    )
)
@click.argument("wikipath", required=False)
def main(wikipath=None):
    preferences = config.read_user_preferences(CONFIG_FILE)
    # if wikipath is specified, it should override
    # the configured paths in the ini file
    if wikipath:
        wikidirs = [wikipath]
    else:
        wikidirs = preferences["wikis"]

    filepaths = []
    for wikidir in wikidirs:
        filepaths.extend(
            map(lambda f: wikidir + "/" + f, preferences['lessons_files'])
        )

    def openfile(fn):
        try:
            f = open(fn, "r")
        except Exception:
            f = StringIO("")
        return f

    lessons_files = map(openfile, filepaths)

    display_message(get_advice(lessons_files))


if __name__ == "__main__":
    main()
