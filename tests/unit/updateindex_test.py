#!/usr/bin/env python
import unittest

import composer.updateindex as updateindex


class WikiPagesKnownValues(unittest.TestCase):
    dummyfiles = [
        'hold on thar.wiki',
        "what's this?.wiki",
        "blah.wiki",
        "blah.wik",
        "blah",
        "blah.wiki.swp",
        "blah.wiki~",
        "bleh.wiki",
    ]
    wikifiles = ['hold on thar', "what's this?", "blah", "bleh"]

    def test_known_values(self):
        """ Check that valid wiki files among known dummy file names are correctly recognized as wiki files """
        wikipages = updateindex.get_wiki_pages_among_files(self.dummyfiles)
        self.assertEqual(set(wikipages), set(self.wikifiles))

    def test_empty_input(self):
        """ Check that an empty list is returned if an empty file list is supplied"""
        wikipages = updateindex.get_wiki_pages_among_files([])
        self.assertEqual(wikipages, [])


class BadInput(unittest.TestCase):
    def test_wiki_pages_among_files_with_bad_input(self):
        """ check that passing an invalid argument (non-list) raises an exception """
        self.assertRaises(Exception, updateindex.get_wiki_pages_among_files, 3)

    def test_wiki_pages_among_files_with_no_input(self):
        """ check that passing no argument raises an exception """
        self.assertRaises(Exception, updateindex.get_wiki_pages_among_files)


if __name__ == '__main__':
    unittest.main()
