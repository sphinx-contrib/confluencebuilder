# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2018-2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
import os
import unittest

def test_override_lang_method(lang):
    return 'custom'

class TestConfluenceLiteralMarkupAdvanced(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = _.prepareConfiguration()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(self.test_dir, 'dataset-advanced')

    def test_highlights_default(self):
        expected = os.path.join(self.test_dir, 'expected-hd')
        doc_dir, doctree_dir = _.prepareDirectories('literal-markup-hd')
        _.buildSphinx(self.dataset, doc_dir, doctree_dir, self.config)
        _.assertExpectedWithOutput(self, 'contents', expected, doc_dir)

    def test_highlights_set(self):
        config = dict(self.config)
        config['highlight_language'] = 'none'

        expected = os.path.join(self.test_dir, 'expected-hs')
        doc_dir, doctree_dir = _.prepareDirectories('literal-markup-hs')
        _.buildSphinx(self.dataset, doc_dir, doctree_dir, config)
        _.assertExpectedWithOutput(self, 'contents', expected, doc_dir)

    def test_override_lang(self):
        config = dict(self.config)
        config['confluence_lang_transform'] = test_override_lang_method

        expected = os.path.join(self.test_dir, 'expected-ol')
        doc_dir, doctree_dir = _.prepareDirectories('literal-markup-ol')
        _.buildSphinx(self.dataset, doc_dir, doctree_dir, config)
        _.assertExpectedWithOutput(self, 'contents', expected, doc_dir)
