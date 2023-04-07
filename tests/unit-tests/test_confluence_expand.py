# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceExpand(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'expand')

    @setup_builder('confluence')
    def test_storage_confluence_expand_directive_expected(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            expand_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'expand'})
            self.assertIsNotNone(expand_macros)
            self.assertEqual(len(expand_macros), 2)

            # expand macro without a title
            expand_macro = expand_macros.pop(0)

            rich_body = expand_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            title = expand_macro.find('ac:parameter', {'ac:name': 'title'})
            self.assertIsNone(title)

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'no title content')

            # expand macro with a title
            expand_macro = expand_macros.pop(0)

            rich_body = expand_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            title = expand_macro.find('ac:parameter', {'ac:name': 'title'})
            self.assertIsNotNone(title)
            self.assertEqual(title.text, 'my title')

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'with title content')
