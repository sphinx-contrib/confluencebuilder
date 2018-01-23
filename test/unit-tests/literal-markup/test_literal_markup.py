# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
"""

from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
import os
import unittest

class TestConfluenceLiteralMarkup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = _.prepareConfiguration()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        dataset = os.path.join(test_dir, 'dataset')
        self.expected = os.path.join(test_dir, 'expected')

        doc_dir, doctree_dir = _.prepareDirectories('literal-markup')
        app = _.prepareSphinx(dataset, doc_dir, doctree_dir, self.config)
        app.build(force_all=True)

        self.doc_dir = doc_dir

    def test_code_blocks(self):
        _.assertExpectedWithOutput(
            self, 'code_blocks', self.expected, self.doc_dir)

    def test_literal_blocks(self):
        _.assertExpectedWithOutput(
            self, 'literal_blocks', self.expected, self.doc_dir)

    def test_literal_includes(self):
        _.assertExpectedWithOutput(
            self, 'literal_includes', self.expected, self.doc_dir)
