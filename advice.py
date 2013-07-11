#!/usr/bin/env python

import re
from random import choice
import sys
from StringIO import StringIO

def extract_lessons(lessons_files):
	# a list containing all lines in a file with leading # removed and trailing \n added
	def extract_lessons_raw(f):
		line = f.readline()
		if not line: return []
		line_fmt = re.sub('^\d+[a-z]?[A-Z]?\. ?', '', line).rstrip('\n') + '\n'
		if line_fmt == '\n': return extract_lessons_raw(f)
		else: return [line_fmt] + extract_lessons_raw(f)

	# combine all lessons from different files into one list
	lessons = map(lambda f: extract_lessons_raw(f), lessons_files)
	lessons = [item for sublist in lessons for item in sublist] # flatten
	return lessons

def get_advice(lessons_files):
	# extract individual lessons from files into a flat list
	lessons = extract_lessons(lessons_files)
	# return lesson by choosing a random element of this list
	if lessons:
		return choice(lessons)
	return ""

if __name__ == '__main__':
	WIKIDIR_TEST = 'tests/testwikis/userwiki'
	WIKIDIR_PRODUCTION = '/Users/siddhartha/log/planner'
	LESSONS_FILES = ('Lessons_Introspective.wiki', 'Lessons_General.wiki', 'Lessons_Advice.wiki', 'Lessons_Experimental.wiki')

	if len(sys.argv) == 1:
		wikidir = WIKIDIR_PRODUCTION
	else:
		if sys.argv[1] == '-t' or sys.argv[1] == '--test':
			wikidir = WIKIDIR_TEST
			print
			print ">>> Operating in TEST mode on planner at location: %s <<<" % wikidir
			print
		else:
			raise Exception("Invalid command line arguments")

	filepaths = map(lambda f: wikidir + '/' + f, LESSONS_FILES)
	def openfile(fn):
		try: f = open(fn, 'r')
		except: f = StringIO('')
		return f
	lessons_files = map(openfile, filepaths)

	print get_advice(lessons_files)
