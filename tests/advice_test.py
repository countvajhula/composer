#!/usr/bin/env python
import unittest
import advice
from StringIO import StringIO


class TestAdvice(unittest.TestCase):
	""" Supported numbering scheme: digit + optional letter. E.g. '12a.' """

	lessons = ['Always do what is right; not because it is easy or prudent, but because it is right.\n', 'Be diligent.\n', 'Routine, routine, routine.\n']
	lessonfile1 = StringIO("1. %s12. %s" % (lessons[0], lessons[1]))
	lessonfile2 = StringIO("1a. %s" % lessons[2])
	emptyfile = StringIO("")
	lesson_nonewline = 'Always add newlines.'
	lessonfile_nonewline = StringIO("1. %s" % lesson_nonewline)
	advicefiles_good = [lessonfile1, lessonfile2]
	advicefiles_empty = [emptyfile]
	advicefiles_nonewline = [lessonfile_nonewline]

	def testAdviceIsProvidedCorrectlyFromFiles(self):
		s = advice.get_advice(self.advicefiles_good)
		self.assertIn(s, self.lessons)

	def testAdviceIsEmptyIfFileIsEmpty(self):
		s = advice.get_advice(self.advicefiles_empty)
		self.assertEqual('', s)

	def testNewlineIsAddedIfNotPresent(self):
		s = advice.get_advice(self.advicefiles_nonewline)
		self.assertEqual(self.lesson_nonewline + '\n', s)

if __name__ == '__main__':
	unittest.main()
