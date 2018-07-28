# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
from sphinxcontrib_confluencebuilder_util import EXT_NAME
import os
import unittest

class TestConfluenceCommon(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = _.prepareConfiguration()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        dataset = os.path.join(test_dir, 'dataset-common')
        self.expected = os.path.join(test_dir, 'expected')

        doc_dir, doctree_dir = _.prepareDirectories('common')
        app = _.prepareSphinx(dataset, doc_dir, doctree_dir, self.config)
        app.build(force_all=True)

        self.doc_dir = doc_dir
        self.app = app

    def _assertExpectedWithOutput(self, name):
        _.assertExpectedWithOutput(self, name, self.expected, self.doc_dir)

    def test_admonitions(self):
        self._assertExpectedWithOutput('admonitions')

    def test_attribution(self):
        self._assertExpectedWithOutput('attribution')

    def test_bibliographic(self):
        self._assertExpectedWithOutput('bibliographic')

    def test_block_quotes(self):
        self._assertExpectedWithOutput('block-quotes')

    def test_citations(self):
        self._assertExpectedWithOutput('citations')

    def test_contents(self):
        #raise unittest.SkipTest('pending pull request #126')
        self._assertExpectedWithOutput('contents')

    def test_definition_lists(self):
        self._assertExpectedWithOutput('definition-lists')

    def test_deprecated(self):
        self._assertExpectedWithOutput('deprecated')

    def test_epigraph(self):
        self._assertExpectedWithOutput('epigraph')

    def test_footnotes(self):
        self._assertExpectedWithOutput('footnotes')

    def test_glossary(self):
        self._assertExpectedWithOutput('glossary')
        self._assertExpectedWithOutput('glossary-ref')

    def test_lists(self):
        self._assertExpectedWithOutput('lists')

    def test_list_table(self):
        self._assertExpectedWithOutput('list-table')

    def test_markup(self):
        self._assertExpectedWithOutput('markup')

    def test_option_lists(self):
        self._assertExpectedWithOutput('option-lists')

    def test_production_list(self):
        self._assertExpectedWithOutput('production-list')

    def test_raw(self):
        self._assertExpectedWithOutput('raw')

    def test_references(self):
        self._assertExpectedWithOutput('references')
        self._assertExpectedWithOutput('references-ref')

    def test_registry(self):
        # validate builder's registration into Sphinx
        if hasattr(self.app, 'extensions'):
            self.assertTrue(EXT_NAME in self.app.extensions.keys())
        else:
            self.assertTrue(EXT_NAME in self.app._extensions.keys())

    def test_sections(self):
        self._assertExpectedWithOutput('sections')

    def test_table(self):
        self._assertExpectedWithOutput('tables')

    def test_transitions(self):
        self._assertExpectedWithOutput('transitions')
