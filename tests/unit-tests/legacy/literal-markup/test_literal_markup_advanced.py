# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2018-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import assertExpectedWithOutput
from tests.lib import build_sphinx
from tests.lib import prepare_conf
import os
import unittest

def test_override_lang_method(lang):
    return 'custom'

class TestConfluenceLiteralMarkupAdvanced(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(self.test_dir, 'dataset-advanced')

    def test_legacy_highlights_default(self):
        expected = os.path.join(self.test_dir, 'expected-hd')
        doc_dir = build_sphinx(self.dataset, config=self.config)
        assertExpectedWithOutput(self, 'index', expected, doc_dir)

    def test_legacy_highlights_set(self):
        config = dict(self.config)
        config['highlight_language'] = 'none'

        expected = os.path.join(self.test_dir, 'expected-hs')
        doc_dir = build_sphinx(self.dataset, config=config)
        assertExpectedWithOutput(self, 'index', expected, doc_dir)

    def test_legacy_override_lang(self):
        config = dict(self.config)
        config['confluence_lang_transform'] = test_override_lang_method

        expected = os.path.join(self.test_dir, 'expected-ol')
        doc_dir = build_sphinx(self.dataset, config=config)
        assertExpectedWithOutput(self, 'index', expected, doc_dir)
