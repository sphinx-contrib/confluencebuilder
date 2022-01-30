# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstAttribution(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceRstAttribution, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'common')
        cls.filenames = [
            'attribution',
        ]

    @setup_builder('confluence')
    def test_storage_rst_attribution(self):
        out_dir = self.build(self.dataset, filenames=self.filenames)

        with parse('attribution', out_dir) as data:
            quote = data.find('blockquote')
            self.assertIsNotNone(quote)

            parts = list(quote.children)
            self.assertEqual(len(parts), 2)

            self.assertEqual(parts[0].text.strip(), 'quote')
            self.assertEqual(parts[1].strip(), '-- source')
