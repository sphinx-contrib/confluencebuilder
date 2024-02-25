# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from bs4 import CData
from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceSphinxCodeblock(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'code-block'

    @setup_builder('confluence')
    def test_storage_sphinx_codeblock_caption(self):
        out_dir = self.build(self.dataset, filenames=['code-block-caption'])

        with parse('code-block-caption', out_dir) as data:
            title_params = data.find_all('ac:parameter', {'ac:name': 'title'})
            self.assertIsNotNone(title_params)
            self.assertEqual(len(title_params), 2)

            title_param = title_params.pop(0)
            self.assertIsNotNone(title_param)
            self.assertEqual(title_param.text, 'code caption test')

    @setup_builder('confluence')
    def test_storage_sphinx_codeblock_default(self):
        out_dir = self.build(self.dataset, filenames=['code-block'])

        with parse('code-block', out_dir) as data:
            code_macros = data.find_all('ac:structured-macro')
            self.assertIsNotNone(code_macros)
            self.assertEqual(len(code_macros), 3)

            for code_macro in code_macros:
                self.assertTrue(code_macro.has_attr('ac:name'))
                self.assertEqual(code_macro['ac:name'], 'code')
                # No theme, by default.
                code_macro_theme = code_macro.find('ac:parameter', {'ac:name': 'theme'})
                self.assertIsNone(code_macro_theme)

            # python block
            python_block = code_macros.pop(0)

            python_block_lang = python_block.find('ac:parameter',
                {'ac:name': 'language'})
            self.assertIsNotNone(python_block_lang)
            self.assertEqual(python_block_lang.text, 'python')

            python_block_linenumbers = python_block.find('ac:parameter',
                {'ac:name': 'linenumbers'})
            self.assertIsNotNone(python_block_linenumbers)
            self.assertEqual(python_block_linenumbers.text, 'true')

            python_block_body = python_block.find('ac:plain-text-body')
            python_block_cdata = next(python_block_body.children, None)
            self.assertIsNotNone(python_block_cdata)
            self.assertTrue(isinstance(python_block_cdata, CData))

            # sql block
            sql_block = code_macros.pop(0)

            sql_block_lang = sql_block.find('ac:parameter',
                {'ac:name': 'language'})
            self.assertIsNotNone(sql_block_lang)
            self.assertEqual(sql_block_lang.text, 'sql')

            sql_block_linenumbers = sql_block.find('ac:parameter',
                {'ac:name': 'linenumbers'})
            self.assertIsNotNone(sql_block_linenumbers)
            self.assertEqual(sql_block_linenumbers.text, 'false')

            sql_block_body = sql_block.find('ac:plain-text-body')
            sql_block_cdata = next(sql_block_body.children, None)
            self.assertIsNotNone(sql_block_cdata)
            self.assertTrue(isinstance(sql_block_cdata, CData))

            # ruby block
            ruby_block = code_macros.pop(0)

            ruby_block_lang = ruby_block.find('ac:parameter',
                {'ac:name': 'language'})
            self.assertIsNotNone(ruby_block_lang)
            self.assertEqual(ruby_block_lang.text, 'ruby')

            ruby_block_linenumbers = ruby_block.find('ac:parameter',
                {'ac:name': 'linenumbers'})
            self.assertIsNotNone(ruby_block_linenumbers)
            self.assertEqual(ruby_block_linenumbers.text, 'false')

            ruby_block_body = ruby_block.find('ac:plain-text-body')
            ruby_block_cdata = next(ruby_block_body.children, None)
            self.assertIsNotNone(ruby_block_cdata)
            self.assertTrue(isinstance(ruby_block_cdata, CData))

            # (check at least one code block's content)
            self.assertEqual(ruby_block_cdata,
                "puts 'this is a print statement!'")

    @setup_builder('confluence')
    def test_storage_sphinx_codeblock_theme_config(self):
        theme = 'Midnight'
        config = dict(self.config)
        config['confluence_code_block_theme'] = theme
        out_dir = self.build(self.dataset, filenames=['code-block'], config=config)

        with parse('code-block', out_dir) as data:
            theme_params = data.find_all('ac:parameter', {'ac:name': 'theme'})
            self.assertIsNotNone(theme_params)
            self.assertEqual(len(theme_params), 3)

            for theme_param in theme_params:
                self.assertIsNotNone(theme_param)
                self.assertEqual(theme_param.text, theme)

    @setup_builder('confluence')
    def test_storage_sphinx_codeblock_theme_override(self):
        expected_theme = 'Eclipse'
        dataset = self.datasets / 'code-block-theme'
        out_dir = self.build(dataset)

        with parse('index', out_dir) as data:
            code_macro_theme = data.find('ac:parameter', {'ac:name': 'theme'})
            self.assertIsNotNone(code_macro_theme)
            self.assertEqual(code_macro_theme.text, expected_theme)
