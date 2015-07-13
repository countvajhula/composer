#!/usr/bin/env python

""" Just a hacked-together script to collect notes from the present week, month, ...,
to help save time on retrospectives """

import os
import config
import advanceplanner
import datetime
import re

PLANNERDAYFILELINK = 'currentday'
PLANNERWEEKFILELINK = 'currentweek'
PLANNERMONTHFILELINK = 'currentmonth'
PLANNERQUARTERFILELINK = 'currentquarter'

def get_filename(wikidir, filelink):
	flink = "%s/%s" % (wikidir, filelink)
	return os.readlink(flink)

def read_file_contents(fnpath):
	fd = open(fnpath, 'r')
	file_contents = fd.read()
	fd.close()
	return file_contents

def extract_log_time_from_text(logtext):
	notes_idx = re.search('NOTES:\n', logtext).end()
	end_idx = re.search('\nTIME', logtext).start()
	log = logtext[notes_idx:end_idx].strip(' \n')
	time_idx = end_idx + logtext[end_idx:].find(':') + 1
	time = logtext[time_idx:].strip(' \n')
	return (log, time)

def get_logs_times_this_week(wikidir):
	""" read currentweek link as filename;
	parse out first day of week from filename;
	open days in order and re search for NOTES. Extract until ^TIME
	exit on file not found error
	return notes separated by lines and headed by dates
	"""
	(logs, times) = ("", [])
	fn = get_filename(wikidir, PLANNERWEEKFILELINK)
	startday_str = re.search("[^\.]*", fn[8:]).group()  # confirm what group does
	curday = datetime.datetime.strptime(startday_str, '%B %d, %Y').date()
	fnpath = "%s/%s.wiki" % (wikidir, curday.strftime('%B %d, %Y').replace(' 0', ' '))
	while True:
		try:
			logtext = read_file_contents(fnpath)
		except:
			break
		(log, time) = extract_log_time_from_text(logtext)
		logs += str(curday) + '\n' + log + '\n\n'
		times.append(time)
		curday += datetime.timedelta(days=1)
		fnpath = "%s/%s.wiki" % (wikidir, curday.strftime('%B %d, %Y').replace(' 0', ' '))  # handle "January 01" as "January 1"
	return (logs, times)

def get_logs_times_this_month(wikidir):
	""" read currentmonth link as filename;
	parse out first week of month from filename;
	open weeks in order and re search for NOTES. Extract until ^TIME
	exit on file not found error
	return notes separated by lines and headed by dates
	"""
	(logs, times) = ("", [])
	fn = get_filename(wikidir, PLANNERMONTHFILELINK)
	month = fn.split()[2].strip(',')
	startday_str = month + " 1, " + fn.split()[3][0:4]
	curday = datetime.datetime.strptime(startday_str, '%B %d, %Y').date()
	fnpath = "%s/Week of %s.wiki" % (wikidir, curday.strftime('%B %d, %Y').replace(' 0', ' '))
	while True:
		try:
			logtext = read_file_contents(fnpath)
		except:
			break
		(log, time) = extract_log_time_from_text(logtext)
		logs += "Week of " + str(curday) + '\n' + log + '\n\n'
		times.append(time)
		curday += datetime.timedelta(days=1)
		while not advanceplanner.newWeekCriteriaMet(curday, datetime.datetime.now()):
			curday += datetime.timedelta(days=1)
		curday += datetime.timedelta(days=1)  # next day is the one we're looking for
		fnpath = "%s/Week of %s.wiki" % (wikidir, curday.strftime('%B %d, %Y').replace(' 0', ' '))
	return (logs, times)

def get_logs_times_this_quarter(wikidir):
	""" read currentquarter link as filename;
	parse out first month of quarter from filename;
	open months in order and re search for NOTES. Extract until ^TIME
	exit on file not found error
	return notes separated by lines and headed by dates
	"""
	(logs, times) = ("", [])
	fn = get_filename(wikidir, PLANNERQUARTERFILELINK)
	quarter = fn.split()[0]
	if quarter == 'Q1':
		month = 'January'
	elif quarter == 'Q2':
		month = 'April'
	elif quarter == 'Q3':
		month = 'July'
	elif quarter == 'Q4':
		month = 'October'
	else:
		raise Exception("Quarter filename not recognized! Must be e.g. 'Q1 2014'")
	startmonth_str = month + ", " + fn.split()[1][0:4]
	curday = datetime.datetime.strptime(startmonth_str, '%B, %Y').date()
	fnpath = "%s/Month of %s.wiki" % (wikidir, curday.strftime('%B, %Y'))
	while True:
		try:
			logtext = read_file_contents(fnpath)
		except:
			break
		(log, time) = extract_log_time_from_text(logtext)
		logs += "Month of " + curday.strftime('%B, %Y') + '\n' + log + '\n\n'
		times.append(time)
		curday = datetime.date(curday.year, curday.month + 1, curday.day)  # not robust to wraparounds but unnecessary here
		fnpath = "%s/Month of %s.wiki" % (wikidir, curday.strftime('%B, %Y'))
	return (logs, times)

if __name__ == '__main__':
	wikidirs = config.PRODUCTION_WIKIDIRS
	for wikidir in wikidirs:
		(weeklogs, weektimes) = get_logs_times_this_week(wikidir)
		(monthlogs, monthtimes) = get_logs_times_this_month(wikidir)
		(quarterlogs, quartertimes) = get_logs_times_this_quarter(wikidir)
		print "Daily logs for the past week (%s)" % wikidir
		print weeklogs
		print "Daily Times:"
		print weektimes
		print
		print "Weekly logs for the past month (%s)" % wikidir
		print monthlogs
		print "Weekly Times:"
		print monthtimes
		print
		print "Monthly logs for the past quarter (%s)" % wikidir
		print quarterlogs
		print "Monthly Times:"
		print quartertimes
		print

