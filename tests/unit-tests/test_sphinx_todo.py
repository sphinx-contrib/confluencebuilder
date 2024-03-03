# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceSphinxTodo(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.config['extensions'].append('sphinx.ext.todo')
        cls.dataset = cls.datasets / 'todo'

    @setup_builder('confluence')
    def test_storage_sphinx_todo_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            info_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'info'})
            self.assertEqual(len(info_macros), 0)

    @setup_builder('confluence')
    def test_storage_sphinx_todo_enabled(self):
        config = dict(self.config)
        config['todo_include_todos'] = True

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            info_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'info'})
            self.assertEqual(len(info_macros), 1)

            info_macro = info_macros.pop(0)

            info_macro_title = info_macro.find('ac:parameter',
                {'ac:name': 'title'})
            self.assertIsNotNone(info_macro_title)

            rich_body = info_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            text_contents = rich_body.text.strip()
            self.assertIsNotNone(text_contents)
            self.assertTrue('example message' in text_contents)
