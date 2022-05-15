# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstParsedLiteral(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceRstParsedLiteral, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'rst', 'parsed-literal')

    @setup_builder('confluence')
    def test_storage_rst_parsedliteral_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            container_block = data.find('pre')
            self.assertIsNotNone(container_block)

            styled_markup = container_block.find('strong')
            self.assertIsNotNone(styled_markup)
