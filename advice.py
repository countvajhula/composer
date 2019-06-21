#!/usr/bin/env python

import config
import re
from random import choice
import sys

try:  # py3
	from io import StringIO
except ImportError:  # py2
	from StringIO import StringIO


def extract_lessons(lessons_files):
	# a list containing all lines in a file with leading # removed and trailing \n added
	def extract_lessons_raw(f):
		line = f.readline()
		if not line:
			return []
		line_fmt = re.sub('^\d+[a-z]?[A-Z]?\. ?', '', line)
		if len(line_fmt) <= 1 or line_fmt == line:
			return extract_lessons_raw(f)
		line_fmt = line_fmt.rstrip('\n') + '\n'
		return [line_fmt] + extract_lessons_raw(f)

	# combine all lessons from different files into one list
	lessons = map(extract_lessons_raw, lessons_files)
	lessons = [item for sublist in lessons for item in sublist]  # flatten
	return lessons


def get_advice(lessons_files):
	# extract individual lessons from files into a flat list
	lessons = extract_lessons(lessons_files)
	# return lesson by choosing a random element of this list
	if lessons:
		return choice(lessons)
	return ""


if __name__ == '__main__':
	if len(sys.argv) == 1:
		wikidirs = config.PRODUCTION_WIKIDIRS
	else:
		if sys.argv[1] == '-t' or sys.argv[1] == '--test':
			wikidirs = config.TEST_WIKIDIRS
			print()
			print(">>> Operating in TEST mode on planners at locations: %s <<<" % wikidirs)
			print()
		else:
			raise Exception("Invalid command line arguments")

	filepaths = []
	for wikidir in wikidirs:
		filepaths.extend(map(lambda f: wikidir + '/' + f, config.LESSONS_FILES))

	def openfile(fn):
		try:
			f = open(fn, 'r')
		except Exception:
			f = StringIO('')
		return f

	lessons_files = map(openfile, filepaths)

	print(get_advice(lessons_files))
