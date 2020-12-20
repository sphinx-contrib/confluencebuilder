# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2019-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import assertExpectedWithOutput
from tests.lib import buildSphinx
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
import os
import unittest

class TestConfluenceMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset_base = os.path.join(self.test_dir, 'dataset-metadata')

        self.config = prepareConfiguration()

        doc_dir, doctree_dir = prepareDirectories('metadata')
        self.doc_dir = doc_dir
        self.doctree_dir = doctree_dir

    def test_legacy_metadata(self):
        dataset = os.path.join(self.dataset_base, 'common')
        expected = os.path.join(self.test_dir, 'expected')

        buildSphinx(dataset, self.doc_dir, self.doctree_dir, self.config)
        assertExpectedWithOutput(
            self, 'metadata', expected, self.doc_dir, tpn='index')
