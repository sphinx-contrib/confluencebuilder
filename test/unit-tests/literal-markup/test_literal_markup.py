# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2020 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from pkg_resources import parse_version
from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
from sphinx.__init__ import __version__ as sphinx_version
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
        _.buildSphinx(dataset, doc_dir, doctree_dir, self.config)

        self.doc_dir = doc_dir

    def test_code_blocks(self):
        # skip code-block tests in Sphinx v1.8.x due to regression
        #  https://github.com/sphinx-contrib/confluencebuilder/issues/148
        if parse_version(sphinx_version) < parse_version('2.0'):
            raise unittest.SkipTest('not supported in sphinx-1.8.x')
        _.assertExpectedWithOutput(
            self, 'code_blocks', self.expected, self.doc_dir)

    def test_literal_blocks(self):
        _.assertExpectedWithOutput(
            self, 'literal_blocks', self.expected, self.doc_dir)

    def test_literal_includes(self):
        _.assertExpectedWithOutput(
            self, 'literal_includes', self.expected, self.doc_dir)
