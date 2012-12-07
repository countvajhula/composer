#!/usr/bin/env python

import datetime
import calendar
import os
import sys
from StringIO import StringIO
#from gaia.identity import Identity

""" Rename to advanceplanner """

WIKIDIR = 'output'
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

def buildPeriodTemplate(nextDay, title, entry, periodname, checkpointsfile, periodicfile):
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
	template += "AGENDA:\n\n"
	template += "TODOs:\n\n"
	template += periodname
	for line in periodicfile:
		if line[:3] == '[ ]': template += line
	template += "\n\n"
	template += "NOTES:\n\n\n"
	template += "Time spent on PLANNER: "
	return template

def buildMonthTemplate(nextDay, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = "= %s %d =\n" % (month, year)
	entry = "\t* [[Week of %s %d, %d]]\n" % (month, date, year)
	periodname = "MONTHLYs:\n"
	monthtemplate = buildPeriodTemplate(nextDay, title, entry, periodname, checkpointsfile, periodicfile)
	return monthtemplate

def buildWeekTemplate(nextDay, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
	title += "\n"
	title += "Theme: *WEEK OF THEME*\n"
	entry = "\t* [[%s %d, %d]]\n" % (month, date, year)
	periodname = "WEEKLYs:\n"
	weektemplate = buildPeriodTemplate(nextDay, title, entry, periodname, checkpointsfile, periodicfile)
	return weektemplate

def buildDayTemplate(nextDay, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = ""
	entry = None
	periodicname = "DAILYs:\n"
	daytemplate = buildPeriodTemplate(nextDay, title, entry, periodicname, checkpointsfile, periodicfile)
	return daytemplate

def writeNewMonthTemplate(nextDay, checkpointsfile, periodicfile, outputfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	monthtemplate = buildMonthTemplate(nextDay, checkpointsfile, periodicfile)
	outputfile.write(monthtemplate)

def writeNewWeekTemplate(nextDay, checkpointsfile, periodicfile, outputfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	weektemplate = buildWeekTemplate(nextDay, checkpointsfile, periodicfile)
	outputfile.write(weektemplate)

def writeNewDayTemplate(nextDay, checkpointsfile, periodicfile, outputfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	daytemplate = buildDayTemplate(nextDay, checkpointsfile, periodicfile)
	outputfile.write(daytemplate)

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
		if day.lower() in ('saturday', 'sunday'):
			checkpointsfile = planner.checkpoints_weekend_file
		else:
			checkpointsfile = planner.checkpoints_weekday_file
		periodicfile = planner.periodic_day_file
		dayfile = StringIO() # new buffer
		writeNewDayTemplate(nextDay, checkpointsfile, periodicfile, dayfile)
		planner.dayfile = dayfile
		status = AdvancePlannerStatus.DayAdded

		if newWeekCriteriaMet():
			checkpointsfile = planner.checkpoints_week_file
			periodicfile = planner.periodic_week_file
			weekfile = StringIO() # new buffer
			writeNewWeekTemplate(nextDay, checkpointsfile, periodicfile, weekfile)
			planner.weekfile = weekfile
			status = AdvancePlannerStatus.WeekAdded

			if newMonthCriteriaMet():
				checkpointsfile = planner.checkpoints_month_file
				periodicfile = planner.periodic_month_file
				monthfile = StringIO() # new buffer
				writeNewMonthTemplate(nextDay, checkpointsfile, periodicfile, monthfile)
				planner.monthfile = monthfile
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

def advanceFilesystemPlanner(plannerpath):
	# use a bunch of StringIO buffers for the Planner object
	# populate them here from real files
	# after the advance() returns, the handles will be updated to the (possibly new) buffers
	# save to the known files here

	# CURRENT planner date used here
	planner = Planner()
	planner.date = getPlannerDate(plannerpath)
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

	status = advancePlanner(planner, now=datetime.datetime.now()+datetime.timedelta(hours=5))

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
	if status == AdvancePlannerStatus.DayAdded:
		# write week buffer to existing file
		f = open(weekfn_pre, 'w')
		f.write(planner.weekfile.read())
		f.close()

if __name__ == '__main__':
	advanceFilesystemPlanner(WIKIDIR)

