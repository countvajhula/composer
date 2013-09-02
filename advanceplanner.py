#!/usr/bin/env python

import datetime
import calendar
from StringIO import StringIO
import re
from errors import *
import templates
import utils
#from gaia.identity import Identity


MIN_WEEK_LENGTH = 5

"""
class Task(Identity):
	def __init__(self, name, description=None):
		self.name = name
		if description: self.description = description
		self.done = False
"""

class PeriodAdvanceCriteria(object):
	(Satisfied, DayStillInProgress, PlannerInFuture) = (1,2,3)

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
	while ss != '' and not re.match(r'^[A-Z][A-Z][A-Z ]+:', ss):
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
	nextDay = utils.getNextDay(currentdate)
	if nextDay.day == 1 and newDayCriteriaMet(currentdate, now) == PeriodAdvanceCriteria.Satisfied:
		return PeriodAdvanceCriteria.Satisfied

def newWeekCriteriaMet(currentdate, now):
	# note that these dates are ~next~ day values
	dow = currentdate.strftime('%A')
	year = currentdate.year
	if newMonthCriteriaMet(currentdate, now) or (newDayCriteriaMet(currentdate, now) == PeriodAdvanceCriteria.Satisfied and dow.lower() == 'saturday' and currentdate.day >= MIN_WEEK_LENGTH and calendar.monthrange(year, currentdate.month)[1] - currentdate.day >= MIN_WEEK_LENGTH):
		return PeriodAdvanceCriteria.Satisfied

def newQuarterCriteriaMet(currentdate, now):
	nextDay = utils.getNextDay(currentdate)
	month = nextDay.strftime('%B')
	if newMonthCriteriaMet(currentdate, now) and month.lower() in ('january', 'april', 'july', 'october'):
		return PeriodAdvanceCriteria.Satisfied

def newYearCriteriaMet(currentdate, now):
	nextDay = utils.getNextDay(currentdate)
	month = nextDay.strftime('%B')
	if newQuarterCriteriaMet(currentdate, now) and month.lower() == 'january':
		return PeriodAdvanceCriteria.Satisfied

def newPeriodCriteriaMet(currentPeriod, currentdate, now):
	if currentPeriod == utils.PlannerPeriod.Day:
		return newDayCriteriaMet(currentdate, now)
	if currentPeriod == utils.PlannerPeriod.Week:
		return newWeekCriteriaMet(currentdate, now)
	if currentPeriod == utils.PlannerPeriod.Month:
		return newMonthCriteriaMet(currentdate, now)
	if currentPeriod == utils.PlannerPeriod.Quarter:
		return newQuarterCriteriaMet(currentdate, now)
	if currentPeriod == utils.PlannerPeriod.Year:
		return newYearCriteriaMet(currentdate, now)

def advancePlanner(planner, now=None):
	""" Advance planner state to next day, updating week and month info as necessary. 'now' arg used only for testing
	TODO: use function compositor thingies to de-duplify these
	"""
	#plannerdate = getPlannerDateFromString('November 30, 2012')
	utils.resetHeadsOnPlannerFiles(planner)
	nextDay = utils.getNextDay(planner.date) # the new day to advance to
	nextdow = nextDay.strftime('%A')
	#writeExistingWeekTemplate(nextDay)
	#writeNewMonthTemplate(nextDay)
	#sys.exit(0)
	#(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)

	if not now: now = datetime.datetime.now()

	def get_period_files(currentPeriod):
		if currentPeriod == utils.PlannerPeriod.Day:
			if nextdow.lower() in ('saturday', 'sunday'):
				checkpointsfile = planner.checkpoints_weekend_file
			else:
				checkpointsfile = planner.checkpoints_weekday_file
			periodicfile = planner.periodic_day_file
			logfile = planner.dayfile
		elif currentPeriod == utils.PlannerPeriod.Week:
			checkpointsfile = planner.checkpoints_week_file
			periodicfile = planner.periodic_week_file
			logfile = planner.weekfile
		elif currentPeriod == utils.PlannerPeriod.Month:
			checkpointsfile = planner.checkpoints_month_file
			periodicfile = planner.periodic_month_file
			logfile = planner.monthfile
		elif currentPeriod == utils.PlannerPeriod.Quarter:
			checkpointsfile = planner.checkpoints_quarter_file
			periodicfile = planner.periodic_quarter_file
			logfile = planner.quarterfile
		elif currentPeriod == utils.PlannerPeriod.Year:
			checkpointsfile = planner.checkpoints_year_file
			periodicfile = planner.periodic_year_file
			logfile = planner.yearfile
		return (checkpointsfile, periodicfile, logfile)

	def get_period_name(currentPeriod):
		periods = {utils.PlannerPeriod.Day: 'day', utils.PlannerPeriod.Week: 'week', utils.PlannerPeriod.Month: 'month',
				utils.PlannerPeriod.Quarter: 'quarter', utils.PlannerPeriod.Year: 'year'}
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
			if not checkLogfileCompletion(logfile) and utils.PlannerConfig.LogfileCompletionChecking == utils.PlannerConfig.Strict:
				periodstr = get_period_name(currentPeriod)
				msg = "Looks like you haven't completed your %s's log. Would you like to do that now?" % periodstr
				raise LogfileNotCompletedError(msg, periodstr)
			templates.writeNewTemplate(currentPeriod, nextDay, tasklistfile, logfile, checkpointsfile, periodicfile, daythemesfile)

			if currentPeriod < utils.PlannerPeriod.Year:
				return advancePeriod(currentPeriod)
		elif periodCriteriaMet == PeriodAdvanceCriteria.DayStillInProgress:
			raise DayStillInProgressError("Current day is still in progress! Update after 6pm")
		elif periodCriteriaMet == PeriodAdvanceCriteria.PlannerInFuture:
			raise PlannerIsInTheFutureError("Planner is in the future!")
		else:
			logfile = get_period_files(currentPeriod + 1)[2]
			templates.writeExistingTemplate(currentPeriod + 1, nextDay, logfile)
		return currentPeriod

	status = advancePeriod(utils.PlannerPeriod.Zero)
	if status > utils.PlannerPeriod.Zero:
		planner.date = nextDay

	utils.resetHeadsOnPlannerFiles(planner)
	return status


if __name__ == '__main__':
	pass
