#!/usr/bin/env python

import advanceplanner
import datetime
import re

WIKIDIR = 'tests/testwikis/daywiki'
#WIKIDIR = '/Users/siddhartha/log/planner'
TASKLISTFILE = 'TaskList.wiki'

def getTasksForTomorrow(tasklist):
	tasks = ''
	s = tasklist.readline()
	while s != '' and s[:len('tomorrow')].lower() != 'tomorrow':
		s = tasklist.readline()
	if s == '':
		raise Exception("Error: No 'TOMORROW' section found in your tasklist! Please add one and try again.")
	s = tasklist.readline()
	while s != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
		if s.startswith('['):
			tasks += s
		s = tasklist.readline()
	return tasks

def doPostMortem(todayfile):
	tasks = {'done':'', 'undone':'', 'blocked':''}
	s = todayfile.readline()
	while s != '' and s[:len('agenda')].lower() != 'agenda':
		s = todayfile.readline()
	if s == '':
		raise Exception("Error: No 'AGENDA' section found in your day's tasklist!")
	s = todayfile.readline()
	while s != '' and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
		if s.startswith('[x'):
			tasks['done'] += s
			s = todayfile.readline()
			while s != '' and not s.startswith('[') and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
				tasks['done'] += s
				s = todayfile.readline()
		elif s.startswith('[ ') or s.startswith('[\\'):
			tasks['undone'] += s
			s = todayfile.readline()
			while s != '' and not s.startswith('[') and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
				tasks['undone'] += s
				s = todayfile.readline()
		elif s.startswith('[o'):
			tasks['blocked'] += s
			s = todayfile.readline()
			while s != '' and not s.startswith('[') and not re.match(r'^[A-Z][A-Z][A-Z]+', s):
				tasks['blocked'] += s
				s = todayfile.readline()
		else:
			s = todayfile.readline()
	return tasks

if __name__ == '__main__':
	"""
	check time -- if >18, then
		check if tomorrow not blank:
			-> move tasks to next agenda
		otherwise:
			The tomorrow section is [still] blank. Do you want to add some tasks for tomorrow?
				Y: No problem. Press any key when you are done adding tasks -loop-/
					Add tasks from today
				N: Okay...
		Scan today; classify done and pending tasks.
		If pending tasks found:
			->Move to next day
			Moved pending tasks from today over to tomorrow's agenda
		[Display score for today]
	"""
	plannerdate = advanceplanner.getPlannerDate(WIKIDIR)
	(date, day, month, year) = (plannerdate.day, plannerdate.strftime('%A'), plannerdate.strftime('%B'), plannerdate.year)
	now = datetime.datetime.now()
	today = now.date()

	def newDayCriteriaMet():
		if plannerdate < today:
			return True
		if plannerdate == today:
			if now.hour >= 18:
				return True
			else:
				print "Current day is still in progress! Update after 6pm"
				return False
		else:
			print "Planner is in the future!"
			return False
	
	if newDayCriteriaMet():
		tasklistfn = '%s/%s' % (WIKIDIR, TASKLISTFILE)
		tomorrowstasks = ''
		while len(tomorrowstasks) == 0:
			tasklist = open(tasklistfn, 'r')
			tomorrowstasks = getTasksForTomorrow(tasklist)
			if len(tomorrowstasks) == 0:
				yn = raw_input("The tomorrow section is blank. Do you want to add some tasks for tomorrow?")
				if yn.lower().startswith('y'):
					tasklist.close()
					raw_input('No problem. Press any key when you are done adding tasks...')
				else:
					tasklist.close()
					break
		todayfn = '%s/%s' % (WIKIDIR, '%s %d, %d.wiki' % (month, date, year))
		todayfile = open(todayfn, 'r')
		todaystasks = doPostMortem(todayfile)
		todayfile.close()
		tomorrowstasks = todaystasks['undone'] + tomorrowstasks
		print tomorrowstasks
		#advanceplanner.advanceFilesystemPlanner(WIKIDIR)
