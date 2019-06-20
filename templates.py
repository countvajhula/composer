import re
import datetime
import utils
import scheduling
from errors import *

try:  # py3
	from io import StringIO
except ImportError:  # py2
	from StringIO import StringIO


def doPostMortem(logfile):
	tasks = {'done': '', 'undone': '', 'blocked': ''}
	ss = logfile.readline()
	while ss != '' and ss[:len('agenda')].lower() != 'agenda':
		ss = logfile.readline()
	if ss == '':
		raise LogfileLayoutError("No AGENDA section found in today's log file! Add one and try again.")
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
		# if re.match('^\t{0,8}\[', s):
		if re.match('^\t*\[', ss):
			tasks += ss
		else:
			tasklist_nextday.write(ss)
		ss = tasklist.readline()
	if tasks == '' and utils.PlannerConfig.TomorrowChecking == utils.PlannerConfig.Strict:
		raise TomorrowIsEmptyError("The tomorrow section is blank. Do you want to add some tasks for tomorrow?")
	while ss != '':
		tasklist_nextday.write(ss)
		ss = tasklist.readline()
	tasklist_nextday.seek(0)
	tasklist.seek(0)
	tasklist.truncate(0)
	tasklist.write(tasklist_nextday.read())
	tasklist.seek(0)
	tasks = tasks.strip('\n')
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
		if line[:3] == '[ ]':
			template += line
	template += "\n"
	template += "AGENDA:\n"
	if agenda:
		template += agenda
		template += "\n"
	template += "\n"
	template += periodname
	for line in periodicfile:
		if line[:3] == '[ ]':
			template += line
	template += "\n"
	template += "NOTES:\n\n\n"
	template += "TIME SPENT ON PLANNER: "
	return template


def buildYearTemplate(nextDay, tasklistfile, yearfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = "= %d =\n" % year
	entry = "\t%s [[%s %d]]\n" % (utils.PlannerConfig.PreferredBulletChar, utils.quarter_for_month(month), year)
	periodname = "YEARLYs:\n"
	agenda = ""
	monthtemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodname, checkpointsfile, periodicfile)
	return monthtemplate


def buildQuarterTemplate(nextDay, tasklistfile, quarterfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = "= %s %d =\n" % (utils.quarter_for_month(month), year)
	entry = "\t%s [[Month of %s, %d]]\n" % (utils.PlannerConfig.PreferredBulletChar, month, year)
	periodname = "QUARTERLYs:\n"
	agenda = ""
	monthtemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodname, checkpointsfile, periodicfile)
	return monthtemplate


def buildMonthTemplate(nextDay, tasklistfile, monthfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = "= %s %d =\n" % (month.upper(), year)
	entry = "\t%s [[Week of %s %d, %d]]\n" % (utils.PlannerConfig.PreferredBulletChar, month, date, year)
	periodname = "MONTHLYs:\n"
	agenda = ""
	monthtemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodname, checkpointsfile, periodicfile)
	return monthtemplate


def buildWeekTemplate(nextDay, tasklistfile, weekfile, checkpointsfile, periodicfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	title = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
	if utils.PlannerUserSettings.WeekTheme:
		title += "\n"
		title += "Theme: *WEEK OF %s*\n" % utils.PlannerUserSettings.WeekTheme.upper()
	entry = "\t%s [[%s %d, %d]]\n" % (utils.PlannerConfig.PreferredBulletChar, month, date, year)
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
		if len(theme) > 2:
			return theme

	theme = getDaysTheme(day)
	if theme:
		title += "\n"
		title += "Theme: %s\n" % theme
	entry = None
	periodicname = "DAILYs:\n"
	undone = doPostMortem(dayfile)['undone']
	scheduled = scheduling.getScheduledTasks(tasklistfile, nextDay)
	tomorrow = getTasksForTomorrow(tasklistfile)
	agenda = ''
	if scheduled:
		agenda += scheduled
	if undone:
		if agenda:
			agenda += '\n' + undone
		else:
			agenda += undone
	if tomorrow:
		if agenda:
			agenda += '\n' + tomorrow
		else:
			agenda += tomorrow
	daytemplate = buildPeriodTemplate(nextDay, title, entry, agenda, periodicname, checkpointsfile, periodicfile)
	return daytemplate


def writeNewTemplate(period, nextDay, tasklistfile, logfile, checkpointsfile, periodicfile, daythemesfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	if period == utils.PlannerPeriod.Day:
		template = buildDayTemplate(nextDay, tasklistfile, logfile, checkpointsfile, periodicfile, daythemesfile)
	if period == utils.PlannerPeriod.Week:
		template = buildWeekTemplate(nextDay, tasklistfile, logfile, checkpointsfile, periodicfile)
	if period == utils.PlannerPeriod.Month:
		template = buildMonthTemplate(nextDay, tasklistfile, logfile, checkpointsfile, periodicfile)
	if period == utils.PlannerPeriod.Quarter:
		template = buildQuarterTemplate(nextDay, tasklistfile, logfile, checkpointsfile, periodicfile)
	if period == utils.PlannerPeriod.Year:
		template = buildYearTemplate(nextDay, tasklistfile, logfile, checkpointsfile, periodicfile)
	logfile.seek(0)
	logfile.truncate(0)
	logfile.write(template)
	logfile.seek(0)


def writeExistingYearTemplate(nextDay, yearfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	yearcontents = yearfile.read()
	lastQuarterEntry = 'Q'
	previdx = yearcontents.find(lastQuarterEntry)
	idx = yearcontents.rfind('\n', 0, previdx)
	newyearcontents = yearcontents[:idx + 1] + '\t%s [[%s %d]]\n' % (utils.PlannerConfig.PreferredBulletChar, utils.quarter_for_month(month), year) + yearcontents[idx + 1:]
	yearfile.seek(0)
	yearfile.truncate(0)
	yearfile.write(newyearcontents)
	yearfile.seek(0)


def writeExistingQuarterTemplate(nextDay, quarterfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	quartercontents = quarterfile.read()
	lastMonthEntry = 'Month of'
	previdx = quartercontents.find(lastMonthEntry)
	idx = quartercontents.rfind('\n', 0, previdx)
	newquartercontents = quartercontents[:idx + 1] + '\t%s [[Month of %s, %d]]\n' % (utils.PlannerConfig.PreferredBulletChar, month, year) + quartercontents[idx + 1:]
	quarterfile.seek(0)
	quarterfile.truncate(0)
	quarterfile.write(newquartercontents)
	quarterfile.seek(0)


def writeExistingMonthTemplate(nextDay, monthfile):
	(date, day, month, year) = (nextDay.day, nextDay.strftime('%A'), nextDay.strftime('%B'), nextDay.year)
	monthcontents = monthfile.read()
	lastWeekEntry = 'Week of'
	previdx = monthcontents.find(lastWeekEntry)
	idx = monthcontents.rfind('\n', 0, previdx)
	newmonthcontents = monthcontents[:idx + 1] + '\t%s [[Week of %s %d, %d]]\n' % (utils.PlannerConfig.PreferredBulletChar, month, date, year) + monthcontents[idx + 1:]
	monthfile.seek(0)
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
	newweekcontents = weekcontents[:idx+1] + '\t%s [[%s %d, %d]]\n' % (utils.PlannerConfig.PreferredBulletChar, month, date, year) + weekcontents[idx + 1:]
	weekfile.seek(0)
	weekfile.truncate(0)  # way to close and open an existing handle in different modes?
	weekfile.write(newweekcontents)
	weekfile.seek(0)


def writeExistingTemplate(currentPeriod, nextDay, logfile):
	# if period is DAY, nop
	if currentPeriod == utils.PlannerPeriod.Day:
		return
	if currentPeriod == utils.PlannerPeriod.Week:
		return writeExistingWeekTemplate(nextDay, logfile)
	if currentPeriod == utils.PlannerPeriod.Month:
		return writeExistingMonthTemplate(nextDay, logfile)
	if currentPeriod == utils.PlannerPeriod.Quarter:
		return writeExistingQuarterTemplate(nextDay, logfile)
	if currentPeriod == utils.PlannerPeriod.Year:
		return writeExistingYearTemplate(nextDay, logfile)
