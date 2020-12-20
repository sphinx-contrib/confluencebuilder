# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2019-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import assertExpectedWithOutput
from tests.lib import build_sphinx
from tests.lib import prepare_conf
import os
import unittest

class TestConfluenceMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset_base = os.path.join(self.test_dir, 'dataset-metadata')

        self.config = prepare_conf()

    def test_legacy_metadata(self):
        dataset = os.path.join(self.dataset_base, 'common')
        expected = os.path.join(self.test_dir, 'expected')

        doc_dir = build_sphinx(dataset, config=self.config)
        assertExpectedWithOutput(
            self, 'metadata', expected, doc_dir, tpn='index')
