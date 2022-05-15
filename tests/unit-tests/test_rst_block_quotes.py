# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstBlockQuotes(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceRstBlockQuotes, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'rst', 'block-quotes')

    @setup_builder('confluence')
    def test_storage_rst_block_quotes(self):
        out_dir = self.build(self.dataset)

        css_margin_indent = 'margin-left: 30px'

        with parse('index', out_dir) as data:
            div_tags = data.find_all('div')

            # ensure each div element in this example is indented
            for div in div_tags:
                self.assertTrue(div.has_attr('style'))
                self.assertTrue(css_margin_indent in div['style'])
