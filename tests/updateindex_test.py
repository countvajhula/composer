#!/usr/bin/env python
import unittest
import updateindex

class WikiPagesKnownValues(unittest.TestCase):
	dummyfiles = ['hold on thar.wiki', "what's this?.wiki", "blah.wiki", "blah.wik", "blah", "blah.wiki.swp", "blah.wiki~", "bleh.wiki"]
	wikifiles = ['hold on thar', "what's this?", "blah",  "bleh"]

	def testKnownValues(self):
		""" Check that valid wiki files among known dummy file names are correctly recognized as wiki files """
		wikipages = updateindex.wikipagesamongfiles(self.dummyfiles)
		self.assertEqual(set(wikipages), set(self.wikifiles))
	
	def testEmptyInput(self):
		""" Check that an empty list is returned if an empty file list is supplied"""
		wikipages = updateindex.wikipagesamongfiles([])
		self.assertEqual(wikipages, [])

class BadInput(unittest.TestCase):
	def testWikiPagesAmongFilesWithBadInput(self):
		""" check that passing an invalid argument (non-list) raises an exception """
		self.assertRaises(Exception, updateindex.wikipagesamongfiles, 3)
	
	def testWikiPagesAmongfilesWithNoInput(self):
		""" check that passing no argument raises an exception """
		self.assertRaises(Exception, updateindex.wikipagesamongfiles)


if __name__ == '__main__':
	unittest.main()
