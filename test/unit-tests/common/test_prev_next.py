# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from __future__ import unicode_literals
from sphinx.application import Sphinx
from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
import io
import os
import unittest

class TestConfluencePrevNext(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))

        self.config = _.prepareConfiguration()
        self.dataset = os.path.join(test_dir, 'dataset-prevnext')
        self.expected = os.path.join(test_dir, 'expected')

    def _character_check(self, name, output, expected):
        test_path = os.path.join(output, name + '.conf')
        self.assertTrue(os.path.exists(test_path),
            'missing output file: {}'.format(test_path))

        with io.open(test_path, encoding='utf8') as test_file:
            data = ''.join([o.strip() + '\n' for o in test_file.readlines()])
            for char, count in expected.items():
                found = data.count(char)
                self.assertTrue(data.count(char) == count,
                    'unexpected character ({}) count (expected: {}, found: {}) '
                    'in file: {}'.format(
                        hex(ord(char)), count, found, test_path))

    def test_prevnext_bottom(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'bottom'

        doc_dir, doctree_dir = _.prepareDirectories('prevnext-bottom')

        with _.prepareSphinx(self.dataset, doc_dir, doctree_dir, config) as app:
            app.build(force_all=True)
            self._character_check('index',  doc_dir, {'←': 0, '→': 1})
            self._character_check('middle', doc_dir, {'←': 1, '→': 1})
            self._character_check('final',  doc_dir, {'←': 1, '→': 0})

    def test_prevnext_both(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'both'

        doc_dir, doctree_dir = _.prepareDirectories('prevnext-both')

        with _.prepareSphinx(self.dataset, doc_dir, doctree_dir, config) as app:
            app.build(force_all=True)
            self._character_check('index',  doc_dir, {'←': 0, '→': 2})
            self._character_check('middle', doc_dir, {'←': 2, '→': 2})
            self._character_check('final',  doc_dir, {'←': 2, '→': 0})

    def test_prevnext_none(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = None

        doc_dir, doctree_dir = _.prepareDirectories('prevnext-none')

        with _.prepareSphinx(self.dataset, doc_dir, doctree_dir, config) as app:
            app.build(force_all=True)
            self._character_check('index',  doc_dir, {'←': 0, '→': 0})
            self._character_check('middle', doc_dir, {'←': 0, '→': 0})
            self._character_check('final',  doc_dir, {'←': 0, '→': 0})

    def test_prevnext_top(self):
        config = dict(self.config)
        config['confluence_prev_next_buttons_location'] = 'top'

        doc_dir, doctree_dir = _.prepareDirectories('prevnext-top')

        with _.prepareSphinx(self.dataset, doc_dir, doctree_dir, config) as app:
            app.build(force_all=True)
            self._character_check('index',  doc_dir, {'←': 0, '→': 1})
            self._character_check('middle', doc_dir, {'←': 1, '→': 1})
            self._character_check('final',  doc_dir, {'←': 1, '→': 0})
