# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2019-2020 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
from sphinx.errors import SphinxWarning
import os
import unittest

class TestConfluenceMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset_base = os.path.join(self.test_dir, 'dataset-metadata')

        self.config = _.prepareConfiguration()

        doc_dir, doctree_dir = _.prepareDirectories('metadata')
        self.doc_dir = doc_dir
        self.doctree_dir = doctree_dir

    def test_metadata(self):
        dataset = os.path.join(self.dataset_base, 'common')
        expected = os.path.join(self.test_dir, 'expected')

        _.buildSphinx(dataset, self.doc_dir, self.doctree_dir, self.config)
        _.assertExpectedWithOutput(
            self, 'metadata', expected, self.doc_dir, tpn='index')
