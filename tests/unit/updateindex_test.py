#!/usr/bin/env python
import os
import pytest
from mock import patch

from composer.updateindex import (
    get_files,
    format_for_display,
    is_wiki,
    prepare_index,
    Index,
    PreIndex,
)


class TestGetFiles(object):
    dummypath = '/dummy/path'
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
    wiki_titles = ['hold on thar', "what's this?", "blah", "bleh"]
    wiki_files = [
        'hold on thar.wiki',
        "what's this?.wiki",
        "blah.wiki",
        "bleh.wiki",
    ]

    def _all_files(self):
        return [os.path.join(self.dummypath, f) for f in self.dummyfiles]

    def _wiki_files(self):
        return [os.path.join(self.dummypath, f) for f in self.wiki_files]

    @patch('composer.updateindex.os')
    def test_get_files(self, mock_os):
        """Check that valid wiki files among known dummy file names are
        correctly recognized as wiki files
        """
        mock_os.listdir.return_value = self.dummyfiles
        mock_os.path.join.side_effect = os.path.join
        wikipages = get_files(self.dummypath)
        expected = self._all_files()
        assert set(wikipages) == set(expected)

    @patch('composer.updateindex.os')
    def test_empty_dir(self, mock_os):
        """Check that an empty list is returned if an empty file list is
        supplied
        """
        mock_os.listdir.return_value = []
        wikipages = get_files(self.dummypath)
        assert list(wikipages) == []

    @patch('composer.updateindex.os')
    def test_of_type(self, mock_os):
        mock_os.listdir.return_value = self.dummyfiles
        mock_os.path.join.side_effect = os.path.join
        wikipages = get_files(self.dummypath, is_wiki)
        expected = self._wiki_files()
        assert set(wikipages) == set(expected)


class TestFormatForDisplay(object):
    dummypath = '/dummy/path'

    def _wiki_file(self, filename):
        return os.path.join(self.dummypath, filename)

    @pytest.mark.parametrize(
        "filename, entry",
        [
            ("hold on thar.wiki", "\t* [[hold on thar]]\n"),
            ("what's this?.wiki", "\t* [[what's this?]]\n"),
            ("blah.wiki", "\t* [[blah]]\n"),
            ("bleh.wiki", "\t* [[bleh]]\n"),
        ],
    )
    def test_format_for_display(self, filename, entry):
        page = self._wiki_file(filename)
        result = format_for_display(page)
        assert result == entry


class TestPrepareIndex(object):
    dummypath = '/dummy/path'

    def test_prepare_index(self):
        contents = ['a', 'c', 'b']
        index_name = 'by date'
        preindex = PreIndex(index_name, None, False)
        path = self.dummypath
        filename = os.path.join(path, "Pages_By date.wiki")
        file_prefix = 'pages'
        root_title = 'index'
        result = prepare_index(
            contents, path, file_prefix, root_title, preindex
        )
        formatted_entries = ['\t* [[a]]\n', '\t* [[b]]\n', '\t* [[c]]\n']
        expected = Index(
            index_name, "= INDEX (BY DATE) =", formatted_entries, filename
        )
        assert result == expected
