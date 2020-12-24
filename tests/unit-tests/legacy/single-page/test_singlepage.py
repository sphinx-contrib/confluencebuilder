# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import assertExpectedWithOutput
from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest

class TestConfluenceSinglePage(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_legacy_singlepage_default(self):
        dataset = os.path.join(self.test_dir, 'dataset')
        expected = os.path.join(self.test_dir, 'expected')
        doc_dir = build_sphinx(dataset, config=self.config, builder='singleconfluence')

        assertExpectedWithOutput(self, 'index', expected, doc_dir)

    def test_legacy_singlepage_numbered(self):
        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered')
        doc_dir = build_sphinx(dataset, config=self.config, builder='singleconfluence')

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
