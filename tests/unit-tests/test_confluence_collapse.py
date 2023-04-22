# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceCollapse(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'collapse')

    @setup_builder('confluence')
    def test_storage_confluence_collapse(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            expand_macro = data.find('ac:structured-macro',
                {'ac:name': 'expand'})
            self.assertIsNotNone(expand_macro)

            rich_body = expand_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            text_contents = rich_body.text.strip()
            self.assertIsNotNone(text_contents)
            self.assertTrue('collapsed paragraph' in text_contents)
