# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceExpand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'expand')

    def test_storage_confluence_expand_directive_expected(self):
        out_dir = build_sphinx(self.dataset, config=self.config)

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
