#!/usr/bin/env python
import unittest
import advice

try:  # py3
	from io import StringIO
except ImportError:  # py2
	from StringIO import StringIO


class TestAdvice(unittest.TestCase):
	""" Supported numbering scheme: digit + optional letter. E.g. '12a.' """

	lessons = ['Always do what is right; not because it is easy or prudent, but because it is right.\n', 'Be diligent.\n', 'Routine, routine, routine.\n']
	lesson_nonewline = 'Always add newlines.'
	lessonfile1 = StringIO("1. %s12. %s" % (lessons[0], lessons[1]))
	lessonfile2 = StringIO("1a. %s" % lessons[2])
	lessonfile_nonewline = StringIO("1. %s" % lesson_nonewline)
	lessonfile_newlines = StringIO("1. %s\n\n2. %s\n3. %s" % (lessons[0], lessons[0], lessons[0]))
	lessonfile_misctext = StringIO("TIPS\n1.%s" % lessons[0])
	emptyfile = StringIO("")
	advicefiles_good = [lessonfile1, lessonfile2]
	advicefiles_empty = [emptyfile]
	advicefiles_nonewline = [lessonfile_nonewline]
	advicefiles_newlines = [lessonfile_newlines]

	def testAdviceIsProvidedCorrectlyFromFiles(self):
		s = advice.get_advice(self.advicefiles_good)
		self.assertIn(s, self.lessons)

	def testAdviceIsEmptyIfFileIsEmpty(self):
		s = advice.get_advice(self.advicefiles_empty)
		self.assertEqual('', s)

	def testNewlineIsAddedIfNotPresent(self):
		s = advice.get_advice(self.advicefiles_nonewline)
		self.assertEqual(self.lesson_nonewline + '\n', s)

	def testHangingNewlinesAreIgnored(self):
		lessons = advice.extract_lessons(self.advicefiles_newlines)
		self.assertEqual(len(lessons), 3)

	def testNonLessonTextIsIgnored(self):
		lessons = advice.extract_lessons([self.lessonfile_misctext])
		self.assertEqual(lessons, [self.lessons[0]])


if __name__ == '__main__':
	unittest.main()
