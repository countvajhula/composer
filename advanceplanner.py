#!/usr/bin/env python

import datetime
import calendar
import os
import sys
from StringIO import StringIO
import re
#from gaia.identity import Identity


#WIKIDIR = '/Users/siddhartha/log/planner'
WIKIDIR = 'tests/testwikis/userwiki'
PLANNERTASKLISTFILELINK = 'TaskList.wiki'
PLANNERDAYFILELINK = 'currentday'
PLANNERWEEKFILELINK = 'currentweek'
PLANNERMONTHFILELINK = 'currentmonth'
CHECKPOINTSWEEKDAYFILE = 'Checkpoints_Weekday.wiki'
CHECKPOINTSWEEKENDFILE = 'Checkpoints_Weekend.wiki'
CHECKPOINTSWEEKFILE = 'Checkpoints_Week.wiki'
CHECKPOINTSMONTHFILE = 'Checkpoints_Month.wiki'
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

class AdvancePlannerStatus(object):
	(NoneAdded, DayAdded, WeekAdded, MonthAdded) = (0,1,2,3)

class PlannerConfig(object):
	(Strict, Lax) = (1,2)
	TomorrowChecking = Strict
	LogfileCompletionChecking = Strict

class PeriodAdvanceCriteria(object):
	(Satisfied, DayStillInProgress, PlannerInFuture) = (1,2,3)

class Planner(object):
	def __init__(self):
		self.date = None
		self.tasklistfile = None
		self.dayfile = None
		self.weekfile = None
		self.monthfile = None
		self.checkpoints_weekday_file = None
		self.checkpoints_weekend_file = None
		self.checkpoints_week_file = None
		self.checkpoints_month_file = None
		self.periodic_day_file = None
		self.periodic_week_file = None
		self.periodic_month_file = None

class DayStillInProgressError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class PlannerIsInTheFutureError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class TomorrowIsEmptyError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class LogfileNotCompletedError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class DayLogfileNotCompletedError(LogfileNotCompletedError):
	def __init__(self, value):
		super(DayLogfileNotCompletedError, self).__init__(value)
		self.type = 'day'

class WeekLogfileNotCompletedError(LogfileNotCompletedError):
	def __init__(self, value):
		super(WeekLogfileNotCompletedError, self).__init__(value)
		self.type = 'week'

class MonthLogfileNotCompletedError(LogfileNotCompletedError):
	def __init__(self, value):
		super(MonthLogfileNotCompletedError, self).__init__(value)
		self.type = 'month'

class DateFormatError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class BlockedTaskNotScheduledError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class TasklistLayoutError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class LogfileLayoutError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class PlannerStateError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class SimulationPassedError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def resetHeadsOnPlannerFiles(planner):
	planner.tasklistfile.seek(0)
	planner.dayfile.seek(0)
	planner.weekfile.seek(0)
	planner.monthfile.seek(0)
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

def getAppropriateYear(month, day, now):
	# if current year would result in negative, then use next year, otherwise current year
	today = now.date()
	date_thisyear = datetime.date(today.year, month, day)
	if date_thisyear < today:
		return today.year + 1
	else:
		return today.year

def getDateForScheduleString(datestr, now=None):
	""" try various acceptable formats and return the first one that works
	Returns both a specific python date that can be used as well as a 'standard format' date string
	that unambiguously represents the date """
	if not now: now = datetime.datetime.now()
	date = None
	monthNameToNumber = dict((v.lower(),k) for k,v in enumerate(calendar.month_name))
	monthNumberToName = dict((k,v) for k,v in enumerate(calendar.month_name))
	def getMonthNumber(monthname):
		return monthNameToNumber[monthname.lower()]
	def getMonthName(monthnumber):
		return monthNumberToName[monthnumber]
	dateformat1 = re.compile('^([^\d ]+) (\d\d?)[, ] ?(\d{4})$')
	dateformat2 = re.compile('^(\d\d?) ([^\d,]+)[, ] ?(\d{4})$')
	dateformat3 = re.compile('^([^\d ]+) (\d\d?)$')
	dateformat4 = re.compile('^(\d\d?) ([^\d]+)$')
	dateformat5 = re.compile('^WEEK OF ([^\d ]+) (\d\d?)[, ] ?(\d{4})$')
	dateformat6 = re.compile('^WEEK OF (\d\d?) ([^\d,]+)[, ] ?(\d{4})$')
	dateformat7 = re.compile('^WEEK OF ([^\d ]+) (\d\d?)$')
	dateformat8 = re.compile('^WEEK OF (\d\d?) ([^\d,]+)$')
	dateformat9 = re.compile('^([^\d ]+)[, ] ?(\d{4})$')
	dateformat10 = re.compile('^([^\d ]+)$')
	dateformat11 = re.compile('^(\d\d)/(\d\d)/(\d\d\d\d)$')
	dateformat12 = re.compile('^(\d\d)-(\d\d)-(\d\d\d\d)$')
	if dateformat1.search(datestr):
		(month, day, year) = dateformat1.search(datestr).groups()
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat2.search(datestr):
		(day, month, year) = dateformat2.search(datestr).groups()
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat3.search(datestr):
		(month, day) = dateformat3.search(datestr).groups()
		(monthn, dayn) = (getMonthNumber(month), int(day))
		year = str(getAppropriateYear(monthn, dayn, now))
		date = datetime.datetime.strptime(month+'-'+day+'-'+year, '%B-%d-%Y').date()
		datestr_std = '%s %s, %s' % (month, day, year)
	elif dateformat4.search(datestr):
		(day, month) = dateformat4.search(datestr).groups()
		(monthn, dayn) = (getMonthNumber(month), int(day))
		year = str(getAppropriateYear(monthn, dayn, now))
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
		(month, day) = dateformat7.search(datestr).groups()
		(monthn, dayn) = (getMonthNumber(month), int(day))
		yearn = getAppropriateYear(monthn, dayn, now)
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
		(day, month) = dateformat8.search(datestr).groups()
		(monthn, dayn) = (getMonthNumber(month), int(day))
		yearn = getAppropriateYear(monthn, dayn, now)
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
	elif dateformat10.search(datestr):
		month = dateformat10.search(datestr).groups()[0]
		(monthn, dayn) = (getMonthNumber(month), 1)
		(day, year) = (str(dayn), str(getAppropriateYear(monthn, dayn, now)))
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
				if not ss.startswith('[o'):
					raise BlockedTaskNotScheduledError("Task in SCHEDULED section does not appear to be formatted correctly: " + ss)
				if scheduledate.search(ss):
					datestr = scheduledate.search(ss).groups()[0]
					try:
						matcheddate = getDateForScheduleString(datestr, now)
					except:
						raise
				else:
					raise BlockedTaskNotScheduledError("No scheduled date for blocked task -- add a date for it: " + ss)
				ss = scheduledate.sub('[$' + matcheddate['datestr'] + '$]', ss) # replace with standard format
				tasklist_tidied.write(ss)
				ss = tasklist.readline()
		elif ss.startswith('[o'):
			if scheduledate.search(ss):
				datestr = scheduledate.search(ss).groups()[0]
				try:
					matcheddate = getDateForScheduleString(datestr, now)
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
					matcheddate = getDateForScheduleString(datestr, now)
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
	if ss == '':
		raise LogfileLayoutError("Error: No 'AGENDA' section found in your day's tasklist!")
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

def buildMonthTemplate(nextDay, tasklistfile, monthfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = "= %s %d =\n" % (month, year)
	entry = "\t* [[Week of %s %d, %d]]\n" % (month, date, year)
	periodname = "MONTHLYs:\n"
	agenda = ""
	monthtemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodname, checkpointsfile, periodicfile)
	return monthtemplate

def buildWeekTemplate(nextDay, tasklistfile, weekfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
	title += "\n"
	title += "Theme: *WEEK OF THEME*\n"
	entry = "\t* [[%s %d, %d]]\n" % (month, date, year)
	periodname = "WEEKLYs:\n"
	agenda = ""
	weektemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodname, checkpointsfile, periodicfile)
	return weektemplate

def buildDayTemplate(nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = ""
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

def writeNewMonthTemplate(nextDay, tasklistfile, checkpointsfile, periodicfile, monthfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	monthtemplate = buildMonthTemplate(nextDay, tasklistfile, monthfile, checkpointsfile, periodicfile)
	monthfile.truncate(0)
	monthfile.write(monthtemplate)
	monthfile.seek(0)

def writeNewWeekTemplate(nextDay, tasklistfile, checkpointsfile, periodicfile, weekfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	weektemplate = buildWeekTemplate(nextDay, tasklistfile, weekfile, checkpointsfile, periodicfile)
	weekfile.truncate(0)
	weekfile.write(weektemplate)
	weekfile.seek(0)

def writeNewDayTemplate(nextDay, tasklistfile, checkpointsfile, periodicfile, dayfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	daytemplate = buildDayTemplate(nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile)
	dayfile.truncate(0)
	dayfile.write(daytemplate)
	dayfile.seek(0)

def writeExistingMonthTemplate(nextDay, monthfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	monthcontents = monthfile.read()
	lastWeekEntry = 'Week of'
	previdx = monthcontents.find(lastWeekEntry)
	idx = monthcontents.rfind('\n', 0, previdx)
	newmonthcontents = monthcontents[:idx+1] + '\t* [[Week of %s %d, %d]]\n' % (month, date, year) + monthcontents[idx+1:]
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
	newweekcontents = weekcontents[:idx+1] + '\t* [[%s %d, %d]]\n' % (month, date, year) + weekcontents[idx+1:]
	weekfile.truncate(0) # way to close and open an existing handle in different modes?
	weekfile.write(newweekcontents)
	weekfile.seek(0)

def advancePlanner(planner, now=None):
	""" Advance planner state to next day, updating week and month info as necessary. 'now' arg used only for testing """
	#plannerdate = getPlannerDateFromString('November 30, 2012')
	resetHeadsOnPlannerFiles(planner)
	nextDay = getNextDay(planner.date) # the new day to advance to
	#writeExistingWeekTemplate(nextDay)
	#writeNewMonthTemplate(nextDay)
	#sys.exit(0)
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)

	if not now: now = datetime.datetime.now()
	today = now.date()

	def newDayCriteriaMet():
		if planner.date < today:
			return PeriodAdvanceCriteria.Satisfied
		if planner.date == today:
			if now.hour >= 18:
				return PeriodAdvanceCriteria.Satisfied
			else:
				# current day still in progress
				return PeriodAdvanceCriteria.DayStillInProgress
		else:
			# planner is in the future
			return PeriodAdvanceCriteria.PlannerInFuture

	def newMonthCriteriaMet():
		if date == 1: return PeriodAdvanceCriteria.Satisfied
	
	def newWeekCriteriaMet():
		# note that these dates are ~next~ day values
		if newMonthCriteriaMet() or (day.lower() == 'sunday' and date > MIN_WEEK_LENGTH and calendar.monthrange(year, nextDay.month)[1] - date >= MIN_WEEK_LENGTH-1):
			return PeriodAdvanceCriteria.Satisfied

	status = AdvancePlannerStatus.NoneAdded

	dayCriteriaMet = newDayCriteriaMet()
	if dayCriteriaMet == PeriodAdvanceCriteria.Satisfied:
		tasklistfile = planner.tasklistfile
		if day.lower() in ('saturday', 'sunday'):
			checkpointsfile = planner.checkpoints_weekend_file
		else:
			checkpointsfile = planner.checkpoints_weekday_file
		periodicfile = planner.periodic_day_file
		dayfile = planner.dayfile
		if not checkLogfileCompletion(dayfile) and PlannerConfig.LogfileCompletionChecking == PlannerConfig.Strict:
			raise DayLogfileNotCompletedError("Looks like you haven't completed your day's log. Would you like to do that now?")
		writeNewDayTemplate(nextDay, tasklistfile, checkpointsfile, periodicfile, dayfile)
		#planner.dayfile = dayfile
		status = AdvancePlannerStatus.DayAdded

		weekCriteriaMet = newWeekCriteriaMet()
		if weekCriteriaMet == PeriodAdvanceCriteria.Satisfied:
			checkpointsfile = planner.checkpoints_week_file
			periodicfile = planner.periodic_week_file
			weekfile = planner.weekfile
			if not checkLogfileCompletion(weekfile) and PlannerConfig.LogfileCompletionChecking == PlannerConfig.Strict:
				raise WeekLogfileNotCompletedError("Looks like you haven't completed your week's log. Would you like to do that now?")
			writeNewWeekTemplate(nextDay, tasklistfile, checkpointsfile, periodicfile, weekfile)
			#planner.weekfile = weekfile
			status = AdvancePlannerStatus.WeekAdded

			monthCriteriaMet = newMonthCriteriaMet()
			if monthCriteriaMet == PeriodAdvanceCriteria.Satisfied:
				checkpointsfile = planner.checkpoints_month_file
				periodicfile = planner.periodic_month_file
				monthfile = planner.monthfile
				if not checkLogfileCompletion(monthfile) and PlannerConfig.LogfileCompletionChecking == PlannerConfig.Strict:
					raise MonthLogfileNotCompletedError("Looks like you haven't completed your month's log. Would you like to do that now?")
				writeNewMonthTemplate(nextDay, tasklistfile, checkpointsfile, periodicfile, monthfile)
				#planner.monthfile = monthfile
				status = AdvancePlannerStatus.MonthAdded
			else:
				monthfile = planner.monthfile
				writeExistingMonthTemplate(nextDay, monthfile)
		else:
			weekfile = planner.weekfile
			writeExistingWeekTemplate(nextDay, weekfile)
		planner.date = nextDay

	elif dayCriteriaMet == PeriodAdvanceCriteria.DayStillInProgress:
		raise DayStillInProgressError("Current day is still in progress! Update after 6pm")

	elif dayCriteriaMet == PeriodAdvanceCriteria.PlannerInFuture:
		raise PlannerIsInTheFutureError("Planner is in the future!")

	resetHeadsOnPlannerFiles(planner)
	return status

def advanceFilesystemPlanner(plannerpath, now=None, simulate=False):
	# use a bunch of StringIO buffers for the Planner object
	# populate them here from real files
	# after the advance() returns, the handles will be updated to the (possibly new) buffers
	# save to the known files here

	# CURRENT planner date used here
	planner = Planner()
	planner.date = getPlannerDate(plannerpath)
	tasklistfn = '%s/%s' % (plannerpath, PLANNERTASKLISTFILELINK)
	f = open(tasklistfn, 'r')
	planner.tasklistfile = StringIO(f.read())
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

	status = scheduleTasks(planner, now)
	status = advancePlanner(planner, now)

	nextDay = planner.date
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	# check for possible errors in planner state before making any changes
	if status >= AdvancePlannerStatus.MonthAdded:
		monthfn_post = '%s/Month of %s, %d.wiki' % (plannerpath, month, year)
		if os.path.isfile(monthfn_post): raise PlannerStateError("New month logfile already exists!")
	if status >= AdvancePlannerStatus.WeekAdded:
		weekfn_post = '%s/Week of %s %d, %d.wiki' % (plannerpath, month, date, year)
		if os.path.isfile(weekfn_post): raise PlannerStateError("New week logfile already exists!")
	if status >= AdvancePlannerStatus.DayAdded:
		dayfn_post = '%s/%s %d, %d.wiki' % (plannerpath, month, date, year)
		if os.path.isfile(dayfn_post): raise PlannerStateError("New day logfile already exists!")

	# if this is a simulation, we're good to go - let's break out of the matrix
	if status >= AdvancePlannerStatus.DayAdded and simulate:
		raise SimulationPassedError('All systems GO')

	if status >= AdvancePlannerStatus.MonthAdded:
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
	if status >= AdvancePlannerStatus.WeekAdded:
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
	if status == AdvancePlannerStatus.WeekAdded:
		# write month buffer to existing file
		f = open(monthfn_pre, 'w')
		f.write(planner.monthfile.read())
		f.close()
	if status >= AdvancePlannerStatus.DayAdded:
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
	if status == AdvancePlannerStatus.DayAdded:
		# write week buffer to existing file
		f = open(weekfn_pre, 'w')
		f.write(planner.weekfile.read())
		f.close()
	
	return status

if __name__ == '__main__':
	pass
