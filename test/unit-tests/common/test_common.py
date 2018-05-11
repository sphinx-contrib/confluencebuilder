# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD, see LICENSE.txt for details.
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

    def test_bad_values(self):
        self._assertExpectedWithOutput('badvalues')

    def test_formatting(self):
        self._assertExpectedWithOutput('formatting')

    def test_list(self):
        self._assertExpectedWithOutput('list')

    def test_references(self):
        self._assertExpectedWithOutput('references')

    def test_glossary(self):
        self._assertExpectedWithOutput('glossary')
        self._assertExpectedWithOutput('glossary2')

    def test_registry(self):
        # validate builder's registration into Sphinx
        if hasattr(self.app, 'extensions'):
            self.assertTrue(EXT_NAME in self.app.extensions.keys())
        else:
            self.assertTrue(EXT_NAME in self.app._extensions.keys())

    def test_table(self):
        self._assertExpectedWithOutput('tables')
