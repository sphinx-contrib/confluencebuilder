# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstEpigraph(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceRstEpigraph, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'rst', 'epigraph')

    @setup_builder('confluence')
    def test_storage_rst_epigraph(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            quote = data.find('div')
            self.assertIsNotNone(quote)

            quote_text = quote.find('p')
            self.assertIsNotNone(quote_text)
            self.assertEqual(quote_text.text.strip(), 'quote')

            quote_sep = quote.find('br')
            self.assertIsNotNone(quote_sep)

            quote_source = quote_sep.nextSibling.strip()
            self.assertEqual(quote_source, '— source')
