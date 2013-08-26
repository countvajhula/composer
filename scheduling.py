import datetime
import calendar
from StringIO import StringIO
import re
import utils
from errors import *


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
		date = utils.getNextDay(planner.date)
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
	utils.resetHeadsOnPlannerFiles(planner)

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
	utils.resetHeadsOnPlannerFiles(planner)

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


