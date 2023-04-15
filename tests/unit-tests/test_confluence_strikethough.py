# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceStrikethrough(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'strikethrough')

    @setup_builder('confluence')
    def test_html_confluence_strikethrough(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            strikethrough_elements = data.find_all('s')
            self.assertEqual(len(strikethrough_elements), 1)

            element = strikethrough_elements.pop(0)
            self.assertEqual(element.text, 'test')
