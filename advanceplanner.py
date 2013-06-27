#!/usr/bin/env python

import datetime
import calendar
import os
from StringIO import StringIO
import re
from errors import *
#from gaia.identity import Identity


#WIKIDIR = '/Users/siddhartha/log/planner'
WIKIDIR = 'tests/testwikis/userwiki'
PLANNERTASKLISTFILELINK = 'TaskList.wiki'
PLANNERDAYTHEMESFILELINK = 'DayThemes.wiki'
PLANNERDAYFILELINK = 'currentday'
PLANNERWEEKFILELINK = 'currentweek'
PLANNERMONTHFILELINK = 'currentmonth'
PLANNERQUARTERFILELINK = 'currentquarter'
PLANNERYEARFILELINK = 'currentyear'
CHECKPOINTSWEEKDAYFILE = 'Checkpoints_Weekday.wiki'
CHECKPOINTSWEEKENDFILE = 'Checkpoints_Weekend.wiki'
CHECKPOINTSWEEKFILE = 'Checkpoints_Week.wiki'
CHECKPOINTSMONTHFILE = 'Checkpoints_Month.wiki'
CHECKPOINTSQUARTERFILE = 'Checkpoints_Quarter.wiki'
CHECKPOINTSYEARFILE = 'Checkpoints_Year.wiki'
PERIODICYEARLYFILE = 'Periodic_Yearly.wiki'
PERIODICQUARTERLYFILE = 'Periodic_Quarterly.wiki'
PERIODICMONTHLYFILE = 'Periodic_Monthly.wiki'
PERIODICWEEKLYFILE = 'Periodic_Weekly.wiki'
PERIODICDAILYFILE = 'Periodic_Daily.wiki'
MIN_WEEK_LENGTH = 5

"""
class Task(Identity):
	def __init__(self, name, description=None):
		self.name = name
		if description: self.description = description
		self.done = False
"""

class PlannerPeriod(object):
	(Zero, Day, Week, Month, Quarter, Year) = (0,1,2,3,4,5)

class PlannerConfig(object):
	(Strict, Lax) = (1,2)
	TomorrowChecking = Strict
	LogfileCompletionChecking = Strict
	PreferredBulletChar = '*'

class PlannerUserSettings(object):
	WeekTheme = None

class PeriodAdvanceCriteria(object):
	(Satisfied, DayStillInProgress, PlannerInFuture) = (1,2,3)

class Planner(object):
	def __init__(self):
		self.date = None
		self.tasklistfile = None
		self.daythemesfile = None
		self.dayfile = None
		self.weekfile = None
		self.monthfile = None
		self.quarterfile = None
		self.yearfile = None
		self.checkpoints_weekday_file = None
		self.checkpoints_weekend_file = None
		self.checkpoints_week_file = None
		self.checkpoints_month_file = None
		self.checkpoints_quarter_file = None
		self.checkpoints_year_file = None
		self.periodic_day_file = None
		self.periodic_week_file = None
		self.periodic_month_file = None
		self.periodic_quarter_file = None
		self.periodic_year_file = None

def resetHeadsOnPlannerFiles(planner):
	planner.tasklistfile.seek(0)
	planner.daythemesfile.seek(0)
	planner.dayfile.seek(0)
	planner.weekfile.seek(0)
	planner.monthfile.seek(0)
	planner.quarterfile.seek(0)
	planner.yearfile.seek(0)
	planner.checkpoints_year_file.seek(0)
	planner.periodic_year_file.seek(0)
	planner.checkpoints_quarter_file.seek(0)
	planner.periodic_quarter_file.seek(0)
	planner.checkpoints_month_file.seek(0)
	planner.periodic_month_file.seek(0)
	planner.checkpoints_week_file.seek(0)
	planner.periodic_week_file.seek(0)
	planner.checkpoints_weekday_file.seek(0)
	planner.checkpoints_weekend_file.seek(0)
	planner.periodic_day_file.seek(0)

def getPlannerDateFromString(datestr):
	return datetime.datetime.strptime(datestr, '%B %d, %Y').date()

def getPlannerDate(plannerlocation):
	""" get planner date, currently looks for the file 'currentday', if dne throw exception """
	plannerdatelink = '%s/%s' % (plannerlocation, PLANNERDAYFILELINK)
	plannerdatefn = os.readlink(plannerdatelink)
	pathidx = plannerdatefn.rfind('/')
	datestr = plannerdatefn[pathidx+1:-5] # trim path from beginning and '.wiki' from end
	plannerdate = getPlannerDateFromString(datestr)
	return plannerdate

def getNextDay(date):
	""" Given a date, return the next day by consulting the python date module """
	nextDay = date + datetime.timedelta(days=1)
	return nextDay

def getAppropriateYear(month, day, today):
	# if current year would result in negative, then use next year, otherwise current year
	date_thisyear = datetime.date(today.year, month, day)
	if date_thisyear < today:
		return today.year + 1
	else:
		return today.year

def getDateForScheduleString(datestr, planner=None, now=None):
	""" try various acceptable formats and return the first one that works
	Returns both a specific python date that can be used as well as a 'standard format' date string
	that unambiguously represents the date """
	if not now: now = datetime.datetime.now()
	date = None
	today = now.date()
	monthNameToNumber = dict((v.lower(),k) for k,v in enumerate(calendar.month_name))
	monthNumberToName = dict((k,v) for k,v in enumerate(calendar.month_name))
	def getMonthNumber(monthname):
		return monthNameToNumber[monthname.lower()]
	def getMonthName(monthnumber):
		return monthNumberToName[monthnumber]
	# TODO: change these to annotated regex's
	# MONTH DD, YYYY (w optional space or comma or both)
	dateformat1 = re.compile('^([^\d ]+) (\d\d?)[, ] ?(\d{4})$')
	# DD MONTH, YYYY (w optional space or comma or both)
	dateformat2 = re.compile('^(\d\d?) ([^\d,]+)[, ] ?(\d{4})$')
	# MONTH DD
	dateformat3 = re.compile('^([^\d ]+) (\d\d?)$')
	# DD MONTH
	dateformat4 = re.compile('^(\d\d?) ([^\d]+)$')
	# WEEK OF MONTH DD, YYYY (w optional space or comma or both)
	dateformat5 = re.compile('^WEEK OF ([^\d ]+) (\d\d?)[, ] ?(\d{4})$')
	# WEEK OF DD MONTH, YYYY (w optional space or comma or both)
	dateformat6 = re.compile('^WEEK OF (\d\d?) ([^\d,]+)[, ] ?(\d{4})$')
	# WEEK OF MONTH DD
	dateformat7 = re.compile('^WEEK OF ([^\d ]+) (\d\d?)$')
	# WEEK OF DD MONTH
	dateformat8 = re.compile('^WEEK OF (\d\d?) ([^\d,]+)$')
	# MONTH YYYY (w optional space or comma or both)
	dateformat9 = re.compile('^([^\d ]+)[, ] ?(\d{4})$')
	# MONTH
	dateformat10 = re.compile('^([^\d ]+)$')
	# MM/DD/YYYY
	dateformat11 = re.compile('^(\d\d)/(\d\d)/(\d\d\d\d)$')
	# MM-DD-YYYY
	dateformat12 = re.compile('^(\d\d)-(\d\d)-(\d\d\d\d)$')
	# TOMORROW
	dateformat13 = re.compile('^TOMORROW$')
	# TODO: need a function to test date boundary status and return monthboundary, weekboundary, or dayboundary (default)
	# NEXT WEEK
	dateformat14 = re.compile('^NEXT WEEK$')
	# NEXT MONTH
	dateformat15 = re.compile('^NEXT MONTH$')
	# <DOW>
	dateformat16 = re.compile('^(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)$')
	# <DOW> (abbrv.)
	dateformat17 = re.compile('^(MON|TUE|WED|THU|FRI|SAT|SUN)$')

	if dateformat1.search(datestr):
		(month, day, year) = dateformat1.search(datestr).groups()
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat2.search(datestr):
		(day, month, year) = dateformat2.search(datestr).groups()
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat3.search(datestr):
		if not planner:
			raise RelativeDateError("Relative date found, but no context available")
		(month, day) = dateformat3.search(datestr).groups()
		(monthn, dayn) = (getMonthNumber(month), int(day))
		year = str(getAppropriateYear(monthn, dayn, planner.date))
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat4.search(datestr):
		if not planner:
			raise RelativeDateError("Relative date found, but no context available")
		(day, month) = dateformat4.search(datestr).groups()
		(monthn, dayn) = (getMonthNumber(month), int(day))
		year = str(getAppropriateYear(monthn, dayn, planner.date))
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat5.search(datestr):
		# std = Week of Month dd(sunday/1), yyyy
		(month, day, year) = dateformat5.search(datestr).groups()
		(monthn, dayn, yearn) = (getMonthNumber(month), int(day), int(year))
		date = datetime.date(yearn, monthn, dayn)
		dow = date.strftime('%A')
		if dayn != 1:
			while dow.lower() != 'sunday':
				date = date - datetime.timedelta(days=1)
				dow = date.strftime('%A')
		(month, day, year) = (getMonthName(date.month), str(date.day), str(date.year))
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = 'WEEK OF %s %s, %s' % (month.upper(), day, year)
	elif dateformat6.search(datestr):
		(day, month, year) = dateformat6.search(datestr).groups()
		(monthn, dayn, yearn) = (getMonthNumber(month), int(day), int(year))
		date = datetime.date(yearn, monthn, dayn)
		dow = date.strftime('%A')
		if dayn != 1:
			while dow.lower() != 'sunday':
				date = date - datetime.timedelta(days=1)
				dow = date.strftime('%A')
		(month, day, year) = (getMonthName(date.month), str(date.day), str(date.year))
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = 'WEEK OF %s %s, %s' % (month.upper(), day, year)
	elif dateformat7.search(datestr):
		if not planner:
			raise RelativeDateError("Relative date found, but no context available")
		(month, day) = dateformat7.search(datestr).groups()
		(monthn, dayn) = (getMonthNumber(month), int(day))
		yearn = getAppropriateYear(monthn, dayn, planner.date)
		year = str(yearn)
		date = datetime.date(yearn, monthn, dayn)
		dow = date.strftime('%A')
		if dayn != 1:
			while dow.lower() != 'sunday':
				date = date - datetime.timedelta(days=1)
				dow = date.strftime('%A')
		(month, day, year) = (getMonthName(date.month), str(date.day), str(date.year))
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = 'WEEK OF %s %s, %s' % (month.upper(), day, year)
	elif dateformat8.search(datestr):
		if not planner:
			raise RelativeDateError("Relative date found, but no context available")
		(day, month) = dateformat8.search(datestr).groups()
		(monthn, dayn) = (getMonthNumber(month), int(day))
		yearn = getAppropriateYear(monthn, dayn, planner.date)
		year = str(yearn)
		date = datetime.date(yearn, monthn, dayn)
		dow = date.strftime('%A')
		if dayn != 1:
			while dow.lower() != 'sunday':
				date = date - datetime.timedelta(days=1)
				dow = date.strftime('%A')
		(month, day, year) = (getMonthName(date.month), str(date.day), str(date.year))
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = 'WEEK OF %s %s, %s' % (month.upper(), day, year)
	elif dateformat9.search(datestr):
		(month, year) = dateformat9.search(datestr).groups()
		day = str(1)
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = '%s %s' % (month, year)
	elif dateformat13.search(datestr): #TOMORROW
		if not planner:
			raise RelativeDateError("Relative date found, but no context available")
		date = getNextDay(planner.date)
		(month, day, year) = (getMonthName(date.month).upper(), str(date.day), str(date.year))
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat16.search(datestr): #<DOW> e.g. MONDAY
		if not planner:
			raise RelativeDateError("Relative date found, but no context available")
		dowToSchedule = dateformat16.search(datestr).groups()[0]
		upcomingweek = map(lambda d:planner.date+datetime.timedelta(days=d), range(1,8))
		dow = [d.strftime('%A').upper() for d in upcomingweek]
		date = upcomingweek[dow.index(dowToSchedule)]
		(month, day, year) = (getMonthName(date.month).upper(), str(date.day), str(date.year))
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat17.search(datestr): #<DOW> short e.g. MON
		if not planner:
			raise RelativeDateError("Relative date found, but no context available")
		dowToSchedule = dateformat17.search(datestr).groups()[0]
		upcomingweek = map(lambda d:planner.date+datetime.timedelta(days=d), range(1,8))
		dow = [d.strftime('%a').upper() for d in upcomingweek]
		date = upcomingweek[dow.index(dowToSchedule)]
		(month, day, year) = (getMonthName(date.month).upper(), str(date.day), str(date.year))
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat10.search(datestr): # MONTH, e.g. DECEMBER
		if not planner:
			raise RelativeDateError("Relative date found, but no context available")
		month = dateformat10.search(datestr).groups()[0]
		(monthn, dayn) = (getMonthNumber(month), 1)
		(day, year) = (str(dayn), str(getAppropriateYear(monthn, dayn, planner.date)))
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = '%s %s' % (month, year)
	elif dateformat11.search(datestr):
		(monthn, dayn, yearn) = map(lambda i:int(i), dateformat11.search(datestr).groups())
		(month, day, year) = (getMonthName(monthn).upper(), str(dayn), str(yearn))
		date = datetime.date(yearn, monthn, dayn)
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat12.search(datestr):
		(monthn, dayn, yearn) = map(lambda i:int(i), dateformat12.search(datestr).groups())
		(month, day, year) = (getMonthName(monthn).upper(), str(dayn), str(yearn))
		date = datetime.date(yearn, monthn, dayn)
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat14.search(datestr): #NEXT WEEK
		if not planner:
			raise RelativeDateError("Relative date found, but no context available")
		dowToSchedule = 'SUNDAY' # start of next week
		upcomingweek = map(lambda d:planner.date+datetime.timedelta(days=d), range(1,8))
		dow = [d.strftime('%A').upper() for d in upcomingweek]
		date = upcomingweek[dow.index(dowToSchedule)]
		(month, day, year) = (getMonthName(date.month).upper(), str(date.day), str(date.year))
		datestr_std = 'WEEK OF %s %s, %s' % (month.upper(), day, year)
	elif dateformat15.search(datestr): #NEXT MONTH
		if not planner:
			raise RelativeDateError("Relative date found, but no context available")
		upcomingmonth = map(lambda d:planner.date+datetime.timedelta(days=d), range(1,31))
		dates = [d.day for d in upcomingmonth]
		date = upcomingmonth[dates.index(1)]
		(month, day, year) = (getMonthName(date.month).upper(), str(date.day), str(date.year))
		datestr_std = '%s %s' % (month, year)
	else: raise DateFormatError("Date format does not match any acceptable formats! " + datestr)
	if date:
		return {'date':date, 'datestr':datestr_std}
	return None

def scheduleTasks(planner, now=None):
	# go through TL till SCHEDULED found
	# if [o] then make sure [$$] and parseable
	# move to bottom of scheduled
	# loop through all scheduled till naother section found or eof
	# go through any other section

	if not now: now = datetime.datetime.now()
	resetHeadsOnPlannerFiles(planner)

	tasklist = planner.tasklistfile
	tasklist_tidied = StringIO()
	scheduledtasks = ""
	ss = tasklist.readline()
	scheduledate = re.compile('\[\$?([^\[\$]*)\$?\]$')
	while ss != '':
		# ignore tasks in tomorrow since actively scheduled by you
		if ss[:len('tomorrow')].lower() == 'tomorrow':
			tasklist_tidied.write(ss)
			ss = tasklist.readline()
			while ss != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
				tasklist_tidied.write(ss)
				ss = tasklist.readline()
		elif ss[:len('scheduled')].lower() == 'scheduled':
			tasklist_tidied.write(ss)
			ss = tasklist.readline()
			while ss != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
				if ss.startswith('[o'):
					if scheduledate.search(ss):
						datestr = scheduledate.search(ss).groups()[0]
						try:
							matcheddate = getDateForScheduleString(datestr, planner, now)
						except:
							raise
					else:
						raise BlockedTaskNotScheduledError("No scheduled date for blocked task -- add a date for it: " + ss)
					ss = scheduledate.sub('[$' + matcheddate['datestr'] + '$]', ss) # replace with standard format
					tasklist_tidied.write(ss)
					ss = tasklist.readline()
					while ss.startswith('\t'):
						tasklist_tidied.write(ss)
						ss = tasklist.readline()
				elif ss.startswith('\n'):
					tasklist_tidied.write(ss)
					ss = tasklist.readline()
				else:
					raise BlockedTaskNotScheduledError("Task in SCHEDULED section does not appear to be formatted correctly: " + ss)
		elif ss.startswith('[o'):
			if scheduledate.search(ss):
				datestr = scheduledate.search(ss).groups()[0]
				try:
					matcheddate = getDateForScheduleString(datestr, planner, now)
				except:
					raise
			else:
				raise BlockedTaskNotScheduledError("No scheduled date for blocked task -- add a date for it: " + ss)
			ss = scheduledate.sub('[$' + matcheddate['datestr'] + '$]', ss) # replace with standard format
			scheduledtasks += ss
			ss = tasklist.readline()
			while ss.startswith('\t'):
				scheduledtasks += ss
				ss = tasklist.readline()
		else:
			tasklist_tidied.write(ss)
			ss = tasklist.readline()

	tasklist = tasklist_tidied # tasklist - misplaced scheduled tasks

	# go through TODAY file
	# if [o] then make sure [$$] and parseable
	# move to scheduled
	dayfile = planner.dayfile
	ss = dayfile.readline()
	while ss != '' and ss[:len('agenda')].lower() != 'agenda':
		ss = dayfile.readline()
	if ss == '': raise LogfileLayoutError("No AGENDA section found in today's log file! Add one and try again.")
	ss = dayfile.readline()
	while ss != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
		if ss.startswith('[o'):
			if scheduledate.search(ss):
				datestr = scheduledate.search(ss).groups()[0]
				try:
					matcheddate = getDateForScheduleString(datestr, planner, now)
				except:
					raise
			else:
				raise BlockedTaskNotScheduledError("No scheduled date for blocked task -- add a date for it:" + ss)
			ss = scheduledate.sub('[$' + matcheddate['datestr'] + '$]', ss) # replace with standard format
			scheduledtasks += ss
			ss = dayfile.readline()
			while ss.startswith('\t'):
				scheduledtasks += ss
				ss = dayfile.readline()
		else:
			ss = dayfile.readline()
	# find SCHEDULED section and insert scheduled tasks
	tasklist_tidied = StringIO()
	tasklist.seek(0)
	ss = tasklist.readline()
	while ss != '' and ss[:len('scheduled')].lower() != 'scheduled':
		tasklist_tidied.write(ss)
		ss = tasklist.readline()
	if ss == '': raise TasklistLayoutError("Tasklist SCHEDULED section not found!")
	tasklist_tidied.write(ss)
	ss = tasklist.readline()
	while ss != '' and ss != '\n':
		tasklist_tidied.write(ss)
		ss = tasklist.readline()
	tasklist_tidied.write(scheduledtasks)
	while ss != '':
		tasklist_tidied.write(ss)
		ss = tasklist.readline()
	tasklist = tasklist_tidied
	tasklist.seek(0)
	planner.tasklistfile.truncate(0)
	planner.tasklistfile.write(tasklist.read())
	resetHeadsOnPlannerFiles(planner)

def getScheduledTasks(tasklist, forDay):
	# look at SCHEDULED section in tasklist and return if scheduled for supplied day
	# remove from tasklist
	# Note: schedule tasks should already have been performed on previous day to migrate those tasks to the tasklist
	tasklist_updated = StringIO()
	ss = tasklist.readline()
	while ss != '' and ss[:len('scheduled')].lower() != 'scheduled':
		tasklist_updated.write(ss)
		ss = tasklist.readline()
	tasklist_updated.write(ss)
	if ss == '': raise TasklistLayoutError("No SCHEDULED section found in TaskList!")
	scheduledate = re.compile('\[\$?([^\[\$]*)\$?\]$')
	scheduledtasks = ''
	ss = tasklist.readline()
	while ss != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
		if ss.startswith('[o'):
			if scheduledate.search(ss):
				datestr = scheduledate.search(ss).groups()[0]
				try:
					matcheddate = getDateForScheduleString(datestr)
				except:
					raise
				if forDay >= matcheddate['date']:
					scheduledtasks += ss
					ss = tasklist.readline()
					while ss.startswith('\t'):
						scheduledtasks += ss
						ss = tasklist.readline()
				else:
					tasklist_updated.write(ss)
					ss = tasklist.readline()
			else:
				raise BlockedTaskNotScheduledError('Scheduled task has no date!' + ss)
		else:
			tasklist_updated.write(ss)
			ss = tasklist.readline()
	# copy rest of the file
	while ss != '':
		tasklist_updated.write(ss)
		ss = tasklist.readline()

	tasklist_updated.seek(0)
	tasklist.truncate(0)
	tasklist.write(tasklist_updated.read())
	tasklist.seek(0)
	scheduledtasks = scheduledtasks.strip('\n')
	return scheduledtasks

def checkLogfileCompletion(logfile):
	""" Check the logfile's NOTES section as a determination of whether the log has been completed """
	completed = False
	notes = ''
	ss = logfile.readline()
	while ss != '' and ss[:len('notes')].lower() != 'notes':
		ss = logfile.readline()
	if ss == '':
		raise LogfileLayoutError("Error: No 'NOTES' section found in your log file: " + ss)
	ss = logfile.readline()
	while ss != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
		notes += ss
		ss = logfile.readline()
	if notes.strip('\n ') != '':
		completed = True
	logfile.seek(0)
	return completed

def extractAgendaFromLogfile(logfile):
	""" Go through logfile and extract all tasks under AGENDA """
	agenda = ''
	ss = logfile.readline()
	while ss != '' and ss[:len('agenda')].lower() != 'agenda':
		ss = logfile.readline()
	if ss == '': raise LogfileLayoutError("No AGENDA section found in today's log file! Add one and try again.")
	ss = logfile.readline()
	while ss != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
		agenda += ss
		ss = logfile.readline()
	logfile.seek(0)
	agenda = agenda.strip('\n')
	return agenda

def updateLogfileAgenda(logfile, agenda):
	logfile_updated = StringIO()
	ss = logfile.readline()
	while ss != '' and ss[:len('agenda')].lower() != 'agenda':
		logfile_updated.write(ss)
		ss = logfile.readline()
	if ss == '': raise LogfileLayoutError("No AGENDA section found in today's log file! Add one and try again.")
	logfile_updated.write(ss)
	ss = logfile.readline()
	while ss != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
		logfile_updated.write(ss)
		ss = logfile.readline()
	# don't leave newlines between previous tasks and latest additions
	logfile_updated.seek(-2,1)
	if logfile_updated.read(2) == '\n\n':
		logfile_updated.seek(-1,1)
	logfile_updated.write(agenda)
	logfile_updated.write('\n\n')
	while ss != '':
		logfile_updated.write(ss)
		ss = logfile.readline()

	logfile.truncate(0)
	logfile_updated.seek(0)
	logfile.write(logfile_updated.read())
	logfile.seek(0)

def getTasksForTomorrow(tasklist):
	""" Read the tasklist, parse all tasks under the TOMORROW section and return those,
	and remove them from the tasklist """
	tasks = ''
	tasklist_nextday = StringIO()
	ss = tasklist.readline()
	while ss != '' and ss[:len('tomorrow')].lower() != 'tomorrow':
		tasklist_nextday.write(ss)
		ss = tasklist.readline()
	if ss == '':
		raise TasklistLayoutError("Error: No 'TOMORROW' section found in your tasklist! Please add one and try again.")
	tasklist_nextday.write(ss)
	ss = tasklist.readline()
	while ss != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
		#if re.match('^\t{0,8}\[', s):
		if re.match('^\t*\[', ss):
			tasks += ss
		else:
			tasklist_nextday.write(ss)
		ss = tasklist.readline()
	if tasks == '' and PlannerConfig.TomorrowChecking == PlannerConfig.Strict:
		raise TomorrowIsEmptyError("The tomorrow section is blank. Do you want to add some tasks for tomorrow?")
	while ss != '':
		tasklist_nextday.write(ss)
		ss = tasklist.readline()
	tasklist_nextday.seek(0)
	tasklist.truncate(0)
	tasklist.write(tasklist_nextday.read())
	tasklist.seek(0)
	tasks = tasks.strip('\n')
	return tasks

def doPostMortem(logfile):
	tasks = {'done':'', 'undone':'', 'blocked':''}
	ss = logfile.readline()
	while ss != '' and ss[:len('agenda')].lower() != 'agenda':
		ss = logfile.readline()
	if ss == '': raise LogfileLayoutError("No AGENDA section found in today's log file! Add one and try again.")
	ss = logfile.readline()
	while ss != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
		if ss.startswith('[x') or ss.startswith('[-'):
			tasks['done'] += ss
			ss = logfile.readline()
			while ss != '' and not ss.startswith('[') and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
				tasks['done'] += ss
				ss = logfile.readline()
		elif ss.startswith('[ ') or ss.startswith('[\\'):
			tasks['undone'] += ss
			ss = logfile.readline()
			while ss != '' and not ss.startswith('[') and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
				tasks['undone'] += ss
				ss = logfile.readline()
		elif ss.startswith('[o'):
			tasks['blocked'] += ss
			ss = logfile.readline()
			while ss != '' and not ss.startswith('[') and not re.match(r'^[A-Z][A-Z][A-Z]+', ss):
				tasks['blocked'] += ss
				ss = logfile.readline()
		else:
			ss = logfile.readline()
	logfile.seek(0)
	tasks['done'] = tasks['done'].strip('\n')
	tasks['undone'] = tasks['undone'].strip('\n')
	tasks['blocked'] = tasks['blocked'].strip('\n')
	return tasks

def quarter_for_month(month):
	if month.lower() in ('january', 'february', 'march'):
		return "Q1"
	elif month.lower() in ('april', 'may', 'june'):
		return "Q2"
	elif month.lower() in ('july', 'august', 'september'):
		return "Q3"
	elif month.lower() in ('october', 'november', 'december'):
		return "Q4"

def buildPeriodTemplate(nextDay, title, entry, agenda, periodname, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	template = ""
	if title:
		template = title
		template += "\n"
	if entry:
		template += entry
		template += "\n"
	template += "CHECKPOINTS:\n"
	for line in checkpointsfile:
		if line[:3] == '[ ]': template += line
	template += "\n"
	template += "AGENDA:\n"
	if agenda:
		template += agenda
		template += "\n"
	template += "\n"
	template += periodname
	for line in periodicfile:
		if line[:3] == '[ ]': template += line
	template += "\n"
	template += "NOTES:\n\n\n"
	template += "TIME SPENT ON PLANNER: "
	return template

def buildYearTemplate(nextDay, tasklistfile, yearfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = "= %d =\n" % year
	entry = "\t%s [[%s %d]]\n" % (PlannerConfig.PreferredBulletChar, quarter_for_month(month), year)
	periodname = "YEARLYs:\n"
	agenda = ""
	monthtemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodname, checkpointsfile, periodicfile)
	return monthtemplate

def buildQuarterTemplate(nextDay, tasklistfile, quarterfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = "= %s %d =\n" % (quarter_for_month(month), year)
	entry = "\t%s [[Month of %s, %d]]\n" % (PlannerConfig.PreferredBulletChar, month, year)
	periodname = "QUARTERLYs:\n"
	agenda = ""
	monthtemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodname, checkpointsfile, periodicfile)
	return monthtemplate

def buildMonthTemplate(nextDay, tasklistfile, monthfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = "= %s %d =\n" % (month.upper(), year)
	entry = "\t%s [[Week of %s %d, %d]]\n" % (PlannerConfig.PreferredBulletChar, month, date, year)
	periodname = "MONTHLYs:\n"
	agenda = ""
	monthtemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodname, checkpointsfile, periodicfile)
	return monthtemplate

def buildWeekTemplate(nextDay, tasklistfile, weekfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
	if PlannerUserSettings.WeekTheme:
		title += "\n"
		title += "Theme: *WEEK OF %s*\n" % PlannerUserSettings.WeekTheme.upper()
	entry = "\t%s [[%s %d, %d]]\n" % (PlannerConfig.PreferredBulletChar, month, date, year)
	periodname = "WEEKLYs:\n"
	agenda = ""
	weektemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodname, checkpointsfile, periodicfile)
	return weektemplate

def buildDayTemplate(nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile, daythemesfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = ("= %s %s %d, %d =\n" % (day, month[:3], date, year)).upper()
	def getDaysTheme(day):
		dailythemes = daythemesfile.read().lower()
		theme = dailythemes[dailythemes.index(day.lower()):]
		theme = theme[theme.index(':'):].strip(': ')
		theme = theme[:theme.index('\n')].strip().upper()
		theme = "*" + theme + "*"
		if len(theme) > 2: return theme
	theme = getDaysTheme(day)
	if theme:
		title += "\n"
		title += "Theme: %s\n" % theme
	entry = None
	periodicname = "DAILYs:\n"
	undone = doPostMortem(dayfile)['undone']
	scheduled = getScheduledTasks(tasklistfile, nextDay)
	tomorrow = getTasksForTomorrow(tasklistfile)
	agenda = ''
	if scheduled: agenda += scheduled
	if undone:
		if agenda: agenda += '\n' + undone
		else: agenda += undone
	if tomorrow:
		if agenda: agenda += '\n' + tomorrow
		else: agenda += tomorrow
	daytemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodicname, checkpointsfile, periodicfile)
	return daytemplate

def writeNewTemplate(period, nextDay, tasklistfile, logfile, checkpointsfile, periodicfile, daythemesfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	if period == PlannerPeriod.Day:
		template = buildDayTemplate(nextDay, tasklistfile, logfile, checkpointsfile, periodicfile, daythemesfile)
	if period == PlannerPeriod.Week:
		template = buildWeekTemplate(nextDay, tasklistfile, logfile, checkpointsfile, periodicfile)
	if period == PlannerPeriod.Month:
		template = buildMonthTemplate(nextDay, tasklistfile, logfile, checkpointsfile, periodicfile)
	if period == PlannerPeriod.Quarter:
		template = buildQuarterTemplate(nextDay, tasklistfile, logfile, checkpointsfile, periodicfile)
	if period == PlannerPeriod.Year:
		template = buildYearTemplate(nextDay, tasklistfile, logfile, checkpointsfile, periodicfile)
	logfile.truncate(0)
	logfile.write(template)
	logfile.seek(0)

def writeExistingYearTemplate(nextDay, yearfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	yearcontents = yearfile.read()
	lastQuarterEntry = 'Q'
	previdx = yearcontents.find(lastQuarterEntry)
	idx = yearcontents.rfind('\n', 0, previdx)
	newyearcontents = yearcontents[:idx+1] + '\t%s [[%s %d]]\n' % (PlannerConfig.PreferredBulletChar, quarter_for_month(month), year) + yearcontents[idx+1:]
	yearfile.truncate(0)
	yearfile.write(newyearcontents)
	yearfile.seek(0)

def writeExistingQuarterTemplate(nextDay, quarterfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	quartercontents = quarterfile.read()
	lastMonthEntry = 'Month of'
	previdx = quartercontents.find(lastMonthEntry)
	idx = quartercontents.rfind('\n', 0, previdx)
	newquartercontents = quartercontents[:idx+1] + '\t%s [[Month of %s, %d]]\n' % (PlannerConfig.PreferredBulletChar, month, year) + quartercontents[idx+1:]
	quarterfile.truncate(0)
	quarterfile.write(newquartercontents)
	quarterfile.seek(0)

def writeExistingMonthTemplate(nextDay, monthfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	monthcontents = monthfile.read()
	lastWeekEntry = 'Week of'
	previdx = monthcontents.find(lastWeekEntry)
	idx = monthcontents.rfind('\n', 0, previdx)
	newmonthcontents = monthcontents[:idx+1] + '\t%s [[Week of %s %d, %d]]\n' % (PlannerConfig.PreferredBulletChar, month, date, year) + monthcontents[idx+1:]
	monthfile.truncate(0)
	monthfile.write(newmonthcontents)
	monthfile.seek(0)

def writeExistingWeekTemplate(nextDay, weekfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	weekcontents = weekfile.read()
	previousDay = nextDay - datetime.timedelta(days=1)
	(dateprev, dayprev, monthprev, yearprev) = (previousDay.day, previousDay.strftime('%A'), previousDay.strftime('%B'), previousDay.year)
	previousDayEntry = '%s %d, %d' % (monthprev, dateprev, yearprev)
	previdx = weekcontents.find(previousDayEntry)
	idx = weekcontents.rfind('\n', 0, previdx)
	newweekcontents = weekcontents[:idx+1] + '\t%s [[%s %d, %d]]\n' % (PlannerConfig.PreferredBulletChar, month, date, year) + weekcontents[idx+1:]
	weekfile.truncate(0) # way to close and open an existing handle in different modes?
	weekfile.write(newweekcontents)
	weekfile.seek(0)

def writeExistingTemplate(currentPeriod, nextDay, logfile):
	# if period is DAY, nop
	if currentPeriod == PlannerPeriod.Day:
		return
	if currentPeriod == PlannerPeriod.Week:
		return writeExistingWeekTemplate(nextDay, logfile)
	if currentPeriod == PlannerPeriod.Month:
		return writeExistingMonthTemplate(nextDay, logfile)
	if currentPeriod == PlannerPeriod.Quarter:
		return writeExistingQuarterTemplate(nextDay, logfile)
	if currentPeriod == PlannerPeriod.Year:
		return writeExistingYearTemplate(nextDay, logfile)

def newDayCriteriaMet(currentdate, now):
	today = now.date()
	if currentdate < today:
		return PeriodAdvanceCriteria.Satisfied
	if currentdate == today:
		if now.hour >= 18:
			return PeriodAdvanceCriteria.Satisfied
		else:
			# current day still in progress
			return PeriodAdvanceCriteria.DayStillInProgress
	else:
		# planner is in the future
		return PeriodAdvanceCriteria.PlannerInFuture

def newMonthCriteriaMet(currentdate, now):
	nextDay = getNextDay(currentdate)
	if nextDay.day == 1 and newDayCriteriaMet(currentdate, now) == PeriodAdvanceCriteria.Satisfied:
		return PeriodAdvanceCriteria.Satisfied

def newWeekCriteriaMet(currentdate, now):
	# note that these dates are ~next~ day values
	dow = currentdate.strftime('%A')
	year = currentdate.year
	if newMonthCriteriaMet(currentdate, now) or (newDayCriteriaMet(currentdate, now) == PeriodAdvanceCriteria.Satisfied and dow.lower() == 'saturday' and currentdate.day >= MIN_WEEK_LENGTH and calendar.monthrange(year, currentdate.month)[1] - currentdate.day >= MIN_WEEK_LENGTH):
		return PeriodAdvanceCriteria.Satisfied

def newQuarterCriteriaMet(currentdate, now):
	nextDay = getNextDay(currentdate)
	month = nextDay.strftime('%B')
	if newMonthCriteriaMet(currentdate, now) and month.lower() in ('january', 'april', 'july', 'october'):
		return PeriodAdvanceCriteria.Satisfied

def newYearCriteriaMet(currentdate, now):
	nextDay = getNextDay(currentdate)
	month = nextDay.strftime('%B')
	if newQuarterCriteriaMet(currentdate, now) and month.lower() == 'january':
		return PeriodAdvanceCriteria.Satisfied

def newPeriodCriteriaMet(currentPeriod, currentdate, now):
	if currentPeriod == PlannerPeriod.Day:
		return newDayCriteriaMet(currentdate, now)
	if currentPeriod == PlannerPeriod.Week:
		return newWeekCriteriaMet(currentdate, now)
	if currentPeriod == PlannerPeriod.Month:
		return newMonthCriteriaMet(currentdate, now)
	if currentPeriod == PlannerPeriod.Quarter:
		return newQuarterCriteriaMet(currentdate, now)
	if currentPeriod == PlannerPeriod.Year:
		return newYearCriteriaMet(currentdate, now)

def advancePlanner(planner, now=None):
	""" Advance planner state to next day, updating week and month info as necessary. 'now' arg used only for testing
	TODO: use function compositor thingies to de-duplify these
	"""
	#plannerdate = getPlannerDateFromString('November 30, 2012')
	resetHeadsOnPlannerFiles(planner)
	nextDay = getNextDay(planner.date) # the new day to advance to
	nextdow = nextDay.strftime('%A')
	#writeExistingWeekTemplate(nextDay)
	#writeNewMonthTemplate(nextDay)
	#sys.exit(0)
	#(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)

	if not now: now = datetime.datetime.now()

	def get_period_files(currentPeriod):
		if currentPeriod == PlannerPeriod.Day:
			if nextdow.lower() in ('saturday', 'sunday'):
				checkpointsfile = planner.checkpoints_weekend_file
			else:
				checkpointsfile = planner.checkpoints_weekday_file
			periodicfile = planner.periodic_day_file
			logfile = planner.dayfile
		elif currentPeriod == PlannerPeriod.Week:
			checkpointsfile = planner.checkpoints_week_file
			periodicfile = planner.periodic_week_file
			logfile = planner.weekfile
		elif currentPeriod == PlannerPeriod.Month:
			checkpointsfile = planner.checkpoints_month_file
			periodicfile = planner.periodic_month_file
			logfile = planner.monthfile
		elif currentPeriod == PlannerPeriod.Quarter:
			checkpointsfile = planner.checkpoints_quarter_file
			periodicfile = planner.periodic_quarter_file
			logfile = planner.quarterfile
		elif currentPeriod == PlannerPeriod.Year:
			checkpointsfile = planner.checkpoints_year_file
			periodicfile = planner.periodic_year_file
			logfile = planner.yearfile
		return (checkpointsfile, periodicfile, logfile)

	def get_period_name(currentPeriod):
		periods = {PlannerPeriod.Day: 'day', PlannerPeriod.Week: 'week', PlannerPeriod.Month: 'month',
				PlannerPeriod.Quarter: 'quarter', PlannerPeriod.Year: 'year'}
		return periods[currentPeriod]

	def advancePeriod(currentPeriod):
		""" Recursive function to advance planner by day, week, month, quarter, or year
		as the case may be.
		"""
		periodCriteriaMet = newPeriodCriteriaMet(currentPeriod + 1, planner.date, now)
		if periodCriteriaMet == PeriodAdvanceCriteria.Satisfied:
			currentPeriod += 1
			tasklistfile = planner.tasklistfile
			daythemesfile = planner.daythemesfile
			(checkpointsfile, periodicfile, logfile) = get_period_files(currentPeriod)
			if not checkLogfileCompletion(logfile) and PlannerConfig.LogfileCompletionChecking == PlannerConfig.Strict:
				periodstr = get_period_name(currentPeriod)
				msg = "Looks like you haven't completed your %s's log. Would you like to do that now?" % periodstr
				raise LogfileNotCompletedError(msg, periodstr)
			writeNewTemplate(currentPeriod, nextDay, tasklistfile, logfile, checkpointsfile, periodicfile, daythemesfile)

			if currentPeriod < PlannerPeriod.Year:
				return advancePeriod(currentPeriod)
		elif periodCriteriaMet == PeriodAdvanceCriteria.DayStillInProgress:
			raise DayStillInProgressError("Current day is still in progress! Update after 6pm")
		elif periodCriteriaMet == PeriodAdvanceCriteria.PlannerInFuture:
			raise PlannerIsInTheFutureError("Planner is in the future!")
		else:
			logfile = get_period_files(currentPeriod + 1)[2]
			writeExistingTemplate(currentPeriod + 1, nextDay, logfile)
		return currentPeriod

	status = advancePeriod(PlannerPeriod.Zero)
	if status > PlannerPeriod.Zero:
		planner.date = nextDay

	resetHeadsOnPlannerFiles(planner)
	return status

def constructPlannerFromFileSystem(plannerpath):
	# CURRENT planner date used here
	planner = Planner()
	planner.date = getPlannerDate(plannerpath)
	tasklistfn = '%s/%s' % (plannerpath, PLANNERTASKLISTFILELINK)
	f = open(tasklistfn, 'r')
	planner.tasklistfile = StringIO(f.read())
	f.close()
	daythemesfn = '%s/%s' % (plannerpath, PLANNERDAYTHEMESFILELINK)
	f = open(daythemesfn, 'r')
	planner.daythemesfile = StringIO(f.read())
	f.close()
	dayfn_pre = '%s/%s' % (plannerpath, PLANNERDAYFILELINK)
	dayfn_pre = '%s/%s' % (plannerpath, os.readlink(dayfn_pre))
	f = open(dayfn_pre, 'r')
	planner.dayfile = StringIO(f.read())
	f.close()
	weekfn_pre = '%s/%s' % (plannerpath, PLANNERWEEKFILELINK)
	weekfn_pre = '%s/%s' % (plannerpath, os.readlink(weekfn_pre))
	f = open(weekfn_pre, 'r')
	planner.weekfile = StringIO(f.read())
	f.close()
	monthfn_pre = '%s/%s' % (plannerpath, PLANNERMONTHFILELINK)
	monthfn_pre = '%s/%s' % (plannerpath, os.readlink(monthfn_pre))
	f = open(monthfn_pre, 'r')
	planner.monthfile = StringIO(f.read())
	f.close()
	quarterfn_pre = '%s/%s' % (plannerpath, PLANNERQUARTERFILELINK)
	quarterfn_pre = '%s/%s' % (plannerpath, os.readlink(quarterfn_pre))
	f = open(quarterfn_pre, 'r')
	planner.quarterfile = StringIO(f.read())
	f.close()
	yearfn_pre = '%s/%s' % (plannerpath, PLANNERYEARFILELINK)
	yearfn_pre = '%s/%s' % (plannerpath, os.readlink(yearfn_pre))
	f = open(yearfn_pre, 'r')
	planner.yearfile = StringIO(f.read())
	f.close()

	# daily, weekly, monthly checkpoints, periodic items
	fn = '%s/%s' % (plannerpath, CHECKPOINTSWEEKDAYFILE)
	f = open(fn, 'r')
	planner.checkpoints_weekday_file = StringIO(f.read())
	f.close()
	fn = '%s/%s' % (plannerpath, CHECKPOINTSWEEKENDFILE)
	f = open(fn, 'r')
	planner.checkpoints_weekend_file = StringIO(f.read())
	f.close()
	fn = '%s/%s' % (plannerpath, PERIODICDAILYFILE)
	f = open(fn, 'r')
	planner.periodic_day_file = StringIO(f.read())
	f.close()
	fn = '%s/%s' % (plannerpath, CHECKPOINTSWEEKFILE)
	f = open(fn, 'r')
	planner.checkpoints_week_file = StringIO(f.read())
	f.close()
	fn = '%s/%s' % (plannerpath, PERIODICWEEKLYFILE)
	f = open(fn, 'r')
	planner.periodic_week_file = StringIO(f.read())
	f.close()
	fn = '%s/%s' % (plannerpath, CHECKPOINTSMONTHFILE)
	f = open(fn, 'r')
	planner.checkpoints_month_file = StringIO(f.read())
	f.close()
	fn = '%s/%s' % (plannerpath, PERIODICMONTHLYFILE)
	f = open(fn, 'r')
	planner.periodic_month_file = StringIO(f.read())
	f.close()
	fn = '%s/%s' % (plannerpath, CHECKPOINTSQUARTERFILE)
	f = open(fn, 'r')
	planner.checkpoints_quarter_file = StringIO(f.read())
	f.close()
	fn = '%s/%s' % (plannerpath, PERIODICQUARTERLYFILE)
	f = open(fn, 'r')
	planner.periodic_quarter_file = StringIO(f.read())
	f.close()
	fn = '%s/%s' % (plannerpath, CHECKPOINTSYEARFILE)
	f = open(fn, 'r')
	planner.checkpoints_year_file = StringIO(f.read())
	f.close()
	fn = '%s/%s' % (plannerpath, PERIODICYEARLYFILE)
	f = open(fn, 'r')
	planner.periodic_year_file = StringIO(f.read())
	f.close()

	return planner

def writePlannerToFilesystem(planner, plannerpath):
	tasklistfn = '%s/%s' % (plannerpath, PLANNERTASKLISTFILELINK)
	dayfn_pre = '%s/%s' % (plannerpath, PLANNERDAYFILELINK)
	dayfn_pre = '%s/%s' % (plannerpath, os.readlink(dayfn_pre))
	weekfn_pre = '%s/%s' % (plannerpath, PLANNERWEEKFILELINK)
	weekfn_pre = '%s/%s' % (plannerpath, os.readlink(weekfn_pre))
	monthfn_pre = '%s/%s' % (plannerpath, PLANNERMONTHFILELINK)
	monthfn_pre = '%s/%s' % (plannerpath, os.readlink(monthfn_pre))
	quarterfn_pre = '%s/%s' % (plannerpath, PLANNERQUARTERFILELINK)
	quarterfn_pre = '%s/%s' % (plannerpath, os.readlink(quarterfn_pre))
	yearfn_pre = '%s/%s' % (plannerpath, PLANNERYEARFILELINK)
	yearfn_pre = '%s/%s' % (plannerpath, os.readlink(yearfn_pre))

	f = open(tasklistfn, 'w')
	f.write(planner.tasklistfile.read())
	f.close()
	f = open(yearfn_pre, 'w')
	f.write(planner.yearfile.read())
	f.close()
	f = open(quarterfn_pre, 'w')
	f.write(planner.quarterfile.read())
	f.close()
	f = open(monthfn_pre, 'w')
	f.write(planner.monthfile.read())
	f.close()
	f = open(weekfn_pre, 'w')
	f.write(planner.weekfile.read())
	f.close()
	f = open(dayfn_pre, 'w')
	f.write(planner.dayfile.read())
	f.close()

	resetHeadsOnPlannerFiles(planner)

def advanceFilesystemPlanner(plannerpath, now=None, simulate=False):
	# use a bunch of StringIO buffers for the Planner object
	# populate them here from real files
	# after the advance() returns, the handles will be updated to the (possibly new) buffers
	# save to the known files here

	planner = constructPlannerFromFileSystem(plannerpath)

	status = scheduleTasks(planner, now)
	status = advancePlanner(planner, now)

	tasklistfn = '%s/%s' % (plannerpath, PLANNERTASKLISTFILELINK)
	dayfn_pre = '%s/%s' % (plannerpath, PLANNERDAYFILELINK)
	dayfn_pre = '%s/%s' % (plannerpath, os.readlink(dayfn_pre))
	weekfn_pre = '%s/%s' % (plannerpath, PLANNERWEEKFILELINK)
	weekfn_pre = '%s/%s' % (plannerpath, os.readlink(weekfn_pre))
	monthfn_pre = '%s/%s' % (plannerpath, PLANNERMONTHFILELINK)
	monthfn_pre = '%s/%s' % (plannerpath, os.readlink(monthfn_pre))
	quarterfn_pre = '%s/%s' % (plannerpath, PLANNERQUARTERFILELINK)
	quarterfn_pre = '%s/%s' % (plannerpath, os.readlink(quarterfn_pre))
	yearfn_pre = '%s/%s' % (plannerpath, PLANNERYEARFILELINK)
	yearfn_pre = '%s/%s' % (plannerpath, os.readlink(yearfn_pre))

	nextDay = planner.date
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	# check for possible errors in planner state before making any changes
	if status >= PlannerPeriod.Year:
		yearfn_post = '%s/%d.wiki' % (plannerpath, year)
		if os.path.isfile(yearfn_post): raise PlannerStateError("New year logfile already exists!")
	if status >= PlannerPeriod.Quarter:
		quarterfn_post = '%s/%s %d.wiki' % (plannerpath, quarter_for_month(month), year)
		if os.path.isfile(quarterfn_post): raise PlannerStateError("New quarter logfile already exists!")
	if status >= PlannerPeriod.Month:
		monthfn_post = '%s/Month of %s, %d.wiki' % (plannerpath, month, year)
		if os.path.isfile(monthfn_post): raise PlannerStateError("New month logfile already exists!")
	if status >= PlannerPeriod.Week:
		weekfn_post = '%s/Week of %s %d, %d.wiki' % (plannerpath, month, date, year)
		if os.path.isfile(weekfn_post): raise PlannerStateError("New week logfile already exists!")
	if status >= PlannerPeriod.Day:
		dayfn_post = '%s/%s %d, %d.wiki' % (plannerpath, month, date, year)
		if os.path.isfile(dayfn_post): raise PlannerStateError("New day logfile already exists!")

	# if this is a simulation, we're good to go - let's break out of the matrix
	if status >= PlannerPeriod.Day and simulate:
		raise SimulationPassedError('All systems GO', status)

	if status >= PlannerPeriod.Year:
		# extract new year filename from date
		# write buffer to new file
		# update currentyear symlink
		yearfn_post = '%s/%d.wiki' % (plannerpath, year)
		f = open(yearfn_post, 'w')
		f.write(planner.yearfile.read())
		f.close()
		filelinkfn = '%s/%s' % (plannerpath, PLANNERYEARFILELINK)
		if os.path.islink(filelinkfn): os.remove(filelinkfn)
		os.symlink(yearfn_post[yearfn_post.rfind('/')+1:], filelinkfn) # remove path from filename so it isn't "double counted"
	if status >= PlannerPeriod.Quarter:
		# extract new quarter filename from date
		# write buffer to new file
		# update currentquarter symlink
		quarterfn_post = '%s/%s %d.wiki' % (plannerpath, quarter_for_month(month), year)
		f = open(quarterfn_post, 'w')
		f.write(planner.quarterfile.read())
		f.close()
		filelinkfn = '%s/%s' % (plannerpath, PLANNERQUARTERFILELINK)
		if os.path.islink(filelinkfn): os.remove(filelinkfn)
		os.symlink(quarterfn_post[quarterfn_post.rfind('/')+1:], filelinkfn) # remove path from filename so it isn't "double counted"
	if status == PlannerPeriod.Quarter:
		# write year buffer to existing file
		f = open(yearfn_pre, 'w')
		f.write(planner.yearfile.read())
		f.close()
	if status >= PlannerPeriod.Month:
		# extract new month filename from date
		# write buffer to new file
		# update currentmonth symlink
		monthfn_post = '%s/Month of %s, %d.wiki' % (plannerpath, month, year)
		f = open(monthfn_post, 'w')
		f.write(planner.monthfile.read())
		f.close()
		filelinkfn = '%s/%s' % (plannerpath, PLANNERMONTHFILELINK)
		if os.path.islink(filelinkfn): os.remove(filelinkfn)
		os.symlink(monthfn_post[monthfn_post.rfind('/')+1:], filelinkfn) # remove path from filename so it isn't "double counted"
	if status == PlannerPeriod.Month:
		# write quarter buffer to existing file
		f = open(quarterfn_pre, 'w')
		f.write(planner.quarterfile.read())
		f.close()
	if status >= PlannerPeriod.Week:
		# extract new week filename from date
		# write buffer to new file
		# update currentweek symlink
		weekfn_post = '%s/Week of %s %d, %d.wiki' % (plannerpath, month, date, year)
		f = open(weekfn_post, 'w')
		f.write(planner.weekfile.read())
		f.close()
		filelinkfn = '%s/%s' % (plannerpath, PLANNERWEEKFILELINK)
		if os.path.islink(filelinkfn): os.remove(filelinkfn)
		os.symlink(weekfn_post[weekfn_post.rfind('/')+1:], filelinkfn) # remove path from filename so it isn't "double counted"
	if status == PlannerPeriod.Week:
		# write month buffer to existing file
		f = open(monthfn_pre, 'w')
		f.write(planner.monthfile.read())
		f.close()
	if status >= PlannerPeriod.Day:
		# extract new day filename from date
		# write buffer to new file
		# update currentday symlink
		dayfn_post = '%s/%s %d, %d.wiki' % (plannerpath, month, date, year)
		f = open(dayfn_post, 'w')
		f.write(planner.dayfile.read())
		f.close()
		filelinkfn = '%s/%s' % (plannerpath, PLANNERDAYFILELINK)
		if os.path.islink(filelinkfn): os.remove(filelinkfn)
		os.symlink(dayfn_post[dayfn_post.rfind('/')+1:], filelinkfn) # remove path from filename so it isn't "double counted"
		# in any event if day was advanced, update tasklist
		f = open(tasklistfn, 'w')
		f.write(planner.tasklistfile.read())
		f.close()
	if status == PlannerPeriod.Day:
		# write week buffer to existing file
		f = open(weekfn_pre, 'w')
		f.write(planner.weekfile.read())
		f.close()
	
	return status

if __name__ == '__main__':
	pass
