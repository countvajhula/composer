#!/usr/bin/env python

import datetime
import calendar
import os
import sys
from StringIO import StringIO
import re
#from gaia.identity import Identity


#WIKIDIR = '/Users/siddhartha/log/planner'
WIKIDIR = 'tests/testwikis/daywiki'
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

def getAppropriateYear(date):
	# if current year would result in negative, then use next year, otherwise current year
	pass

def getDateForScheduleString(datestr):
	# try various acceptable formats and return the first one that works
	return datetime.datetime.strptime(datestr, '%B %d, %Y').date() or datetime.datetime.strptime(datestr, '%d %B, %Y').date() # TODO: add more format options

def scheduleTasks(planner):
	# go through TL till SCHEDULED found
	# if [o] then make sure [$$] and parseable
	# move to bottom of scheduled
	# loop through all scheduled till naother section found or eof
	# go through any other section
	tasklist = planner.tasklistfile
	tasklist_tidied = StringIO()
	scheduledtasks = ""
	s = tasklist.readline()
	scheduledate = re.compile('\[\$?([^\[\$]*)\$?\]$')
	while s != '' and s[:len('scheduled')].lower() != 'scheduled':
		if s.startswith('[o'):
			if scheduledate.search(s):
				datestr = scheduledate.search(s).groups()[0]
				matcheddate = getDateForScheduleString(datestr)
				if not matcheddate:
					raise Exception("Invalid format for date in scheduled task - use '<Month> <date>, <year>': " + s)
			else:
				raise Exception("No scheduled date for blocked task -- add a date for it:" + s)
			scheduledtasks += s
			s = tasklist.readline()
			while s.startswith('\t'):
				scheduledtasks += s
				s = tasklist.readline()
		else:
			tasklist_tidied.write(s)
			s = tasklist.readline()
	tasklist_tidied.write(s)
	s = tasklist.readline()
	while s != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
		tasklist_tidied.write(s)
		s = tasklist.readline()
	while s != '':
		if s.startswith('[o'):
			if scheduledate.search(ss):
				datestr = scheduledate.search(s).groups()[0]
				matcheddate = getDateForScheduleString(datestr)
				if not matcheddate:
					raise Exception("Invalid format for date in scheduled task - use '<Month> <date>, <year>': " + s)
			else:
				raise Exception("No scheduled date for blocked task -- add a date for it:" + s)
			scheduledtasks += s
			s = tasklist.readline()
			while s.startswith('\t'):
				scheduledtasks += s
				s = tasklist.readline()
		else:
			tasklist_tidied.write(s)
			s = tasklist.readline()

	tasklist = tasklist_tidied # tasklist - misplaced scheduled tasks

	# go through TODAY file
	# if [o] then make sure [$$] and parseable
	# move to scheduled
	dayfile = planner.dayfile
	s = dayfile.readline()
	while s != '' and s[:len('agenda')].lower() != 'agenda':
		s = dayfile.readline()
	if s == '': raise Exception("No AGENDA section found in today's log file! Add one and try again.")
	s = dayfile.readline()
	while s != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
		if s.startswith('[o'):
			if scheduledate.search(s):
				datestr = scheduledate.search(s).groups()[0]
				matcheddate = getDateForScheduleString(datestr)
				if not matcheddate:
					raise Exception("Invalid format for date in scheduled task - use '<Month> <date>, <year>': " + s)
			else:
				raise Exception("No scheduled date for blocked task -- add a date for it:" + s)
			scheduledtasks += s
			s = tasklist.readline()
			while s.startswith('\t'):
				scheduledtasks += s
				s = tasklist.readline()
		else:
			s = tasklist.readline()
	tasklist.seek(0)
	s = tasklist.readline()
	while s != '' and s[:len('scheduled')].lower() != 'scheduled':
		s = tasklist.readline()
	if s == '': raise Exception("Tasklist SCHEDULED section not found!")
	s = tasklist.readline()
	while s != '' and s != '\n':
		s = tasklist.readline()
	tasklist.write(scheduledtasks)
	tasklist.seek(0)
	#raise Exception("Just because")
	planner.tasklist = tasklist

def getScheduledTasks(tasklist, forDay):
	# look at SCHEDULED section in tasklist and return if scheduled for supplied day
	# remove from tasklist
	# Note: schedule tasks should already have been performed on previous day to migrate those tasks to the tasklist
	tasklist_updated = StringIO()
	s = tasklist.readline()
	while s != '' and s[:len('scheduled')].lower() != 'scheduled':
		tasklist_updated.write(s)
		s = tasklist.readline()
	tasklist_updated.write(s)
	if s == '': raise Exception("No SCHEDULED section found in TaskList!")
	scheduledate = re.compile('\[\$?([^\[\$]*)\$?\]$')
	scheduledtasks = ''
	s = tasklist.readline()
	while s != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
		if s.startswith('[o'):
			if scheduledate.search(s):
				datestr = scheduledate.search(s).groups()[0]
				matcheddate = getDateForScheduleString(datestr)
				if not matcheddate:
					raise Exception("Invalid format for date in scheduled task - use '<Month> <date>, <year>': " + s)
				if forDay > matcheddate:
					scheduledtasks += s
					s = tasklist.readline()
					while s.startswith('\t'):
						scheduledtasks += s
						s = tasklist.readline()
				else:
					tasklist_updated.write(s)
					s = tasklist.readline()
			else:
				raise Exception('Scheduled task has no date!' + s)
		else:
			tasklist_updated.write(s)
			s = tasklist.readline()

	tasklist_updated.seek(0)
	tasklist.truncate(0)
	tasklist.write(tasklist_updated.read())
	tasklist.seek(0)
	scheduledtasks = scheduledtasks.strip('\n')
	return scheduledtasks

def getTasksForTomorrow(tasklist):
	tasks = ''
	s = tasklist.readline()
	while s != '' and s[:len('tomorrow')].lower() != 'tomorrow':
		s = tasklist.readline()
	if s == '':
		raise Exception("Error: No 'TOMORROW' section found in your tasklist! Please add one and try again.")
	s = tasklist.readline()
	while s != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
		#if re.match('^\t{0,8}\[', s):
		if re.match('^\t*\[', s):
			tasks += s
		s = tasklist.readline()
	tasklist.seek(0)
	tasks = tasks.strip('\n')
	return tasks

def doPostMortem(logfile):
	tasks = {'done':'', 'undone':'', 'blocked':''}
	s = logfile.readline()
	while s != '' and s[:len('agenda')].lower() != 'agenda':
		s = logfile.readline()
	if s == '':
		raise Exception("Error: No 'AGENDA' section found in your day's tasklist!")
	s = logfile.readline()
	while s != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
		if s.startswith('[x') or s.startswith('[-'):
			tasks['done'] += s
			s = logfile.readline()
			while s != '' and not s.startswith('[') and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
				tasks['done'] += s
				s = logfile.readline()
		elif s.startswith('[ ') or s.startswith('[\\'):
			tasks['undone'] += s
			s = logfile.readline()
			while s != '' and not s.startswith('[') and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
				tasks['undone'] += s
				s = logfile.readline()
		elif s.startswith('[o'):
			tasks['blocked'] += s
			s = logfile.readline()
			while s != '' and not s.startswith('[') and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
				tasks['blocked'] += s
				s = logfile.readline()
		else:
			s = logfile.readline()
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
	template += "\n\n"
	template += "AGENDA:\n"
	if agenda:
		template += agenda
		template += "\n"
	template += "\n"
	template += periodname
	for line in periodicfile:
		if line[:3] == '[ ]': template += line
	template += "\n\n"
	template += "NOTES:\n\n\n"
	template += "Time spent on PLANNER: "
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

def writeNewWeekTemplate(nextDay, tasklistfile, checkpointsfile, periodicfile, weekfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	weektemplate = buildWeekTemplate(nextDay, tasklistfile, weekfile, checkpointsfile, periodicfile)
	weekfile.truncate(0)
	weekfile.write(weektemplate)

def writeNewDayTemplate(nextDay, tasklistfile, checkpointsfile, periodicfile, dayfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	daytemplate = buildDayTemplate(nextDay, tasklistfile, dayfile, checkpointsfile, periodicfile)
	dayfile.truncate(0)
	dayfile.write(daytemplate)

def updateMonthTemplate(nextDay, monthfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	monthcontents = monthfile.read()
	lastWeekEntry = 'Week of'
	previdx = monthcontents.find(lastWeekEntry)
	idx = monthcontents.rfind('\n', 0, previdx)
	newmonthcontents = monthcontents[:idx+1] + '\t* [[Week of %s %d, %d]]\n' % (month, date, year) + monthcontents[idx+1:]
	return newmonthcontents

def writeExistingMonthTemplate(nextDay, monthfile):
	newmonthcontents = updateMonthTemplate(nextDay, monthfile)
	monthfile.seek(0)
	monthfile.write(newmonthcontents)

def updateWeekTemplate(nextDay, weekfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	weekcontents = weekfile.read()
	previousDay = nextDay - datetime.timedelta(days=1)
	(dateprev, dayprev, monthprev, yearprev) = (previousDay.day, previousDay.strftime('%A'), previousDay.strftime('%B'), previousDay.year)
	previousDayEntry = '%s %d, %d' % (monthprev, dateprev, yearprev)
	previdx = weekcontents.find(previousDayEntry)
	idx = weekcontents.rfind('\n', 0, previdx)
	newweekcontents = weekcontents[:idx+1] + '\t* [[%s %d, %d]]\n' % (month, date, year) + weekcontents[idx+1:]
	return newweekcontents

def writeExistingWeekTemplate(nextDay, weekfile):
	newweekcontents = updateWeekTemplate(nextDay, weekfile)
	weekfile.seek(0) # way to close and open an existing handle in different modes?
	weekfile.write(newweekcontents)

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
			return True
		if planner.date == today:
			if now.hour >= 18:
				return True
			else:
				print "Current day is still in progress! Update after 6pm"
				return False
		else:
			print "Planner is in the future!"
			return False

	def newMonthCriteriaMet():
		if date == 1: return True
	
	def newWeekCriteriaMet():
		# note that these dates are ~next~ day values
		if newMonthCriteriaMet() or (day.lower() == 'sunday' and date > MIN_WEEK_LENGTH and calendar.monthrange(year, nextDay.month)[1] - date >= MIN_WEEK_LENGTH-1):
			return True

	status = AdvancePlannerStatus.NoneAdded

	if newDayCriteriaMet():
		tasklistfile = planner.tasklistfile
		if day.lower() in ('saturday', 'sunday'):
			checkpointsfile = planner.checkpoints_weekend_file
		else:
			checkpointsfile = planner.checkpoints_weekday_file
		periodicfile = planner.periodic_day_file
		dayfile = planner.dayfile
		writeNewDayTemplate(nextDay, tasklistfile, checkpointsfile, periodicfile, dayfile)
		#planner.dayfile = dayfile
		status = AdvancePlannerStatus.DayAdded

		if newWeekCriteriaMet():
			checkpointsfile = planner.checkpoints_week_file
			periodicfile = planner.periodic_week_file
			weekfile = planner.weekfile
			writeNewWeekTemplate(nextDay, tasklistfile, checkpointsfile, periodicfile, weekfile)
			#planner.weekfile = weekfile
			status = AdvancePlannerStatus.WeekAdded

			if newMonthCriteriaMet():
				checkpointsfile = planner.checkpoints_month_file
				periodicfile = planner.periodic_month_file
				monthfile = planner.monthfile
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

	resetHeadsOnPlannerFiles(planner)
	return status

def advanceFilesystemPlanner(plannerpath, now=None):
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

	status = scheduleTasks(planner)
	status = advancePlanner(planner, now)

	nextDay = planner.date
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	if status >= AdvancePlannerStatus.MonthAdded:
		# extract new month filename from date
		# write buffer to new file
		# update currentmonth symlink
		monthfn_post = '%s/Month of %s, %d.wiki' % (plannerpath, month, year)
		if os.path.isfile(monthfn_post): raise Exception("New month logfile already exists!")
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
		if os.path.isfile(weekfn_post): raise Exception("New week logfile already exists!")
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
		if os.path.isfile(dayfn_post): raise Exception("New day logfile already exists!")
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
	advanceFilesystemPlanner(WIKIDIR)

