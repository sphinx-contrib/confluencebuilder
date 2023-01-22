# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2016-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from bs4 import CData
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstLiteral(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'rst', 'literal')

    @setup_builder('confluence')
    def test_storage_rst_literal_blocks(self):
        out_dir = self.build(self.dataset, filenames=['literal-blocks'])

        with parse('literal-blocks', out_dir) as data:
            code_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'code'})
            self.assertIsNotNone(code_macros)
            self.assertEqual(len(code_macros), 4)

            # ensure each code block has cdata content
            for code_macro in code_macros:
                code_body = code_macro.find('ac:plain-text-body')
                cdata_block = next(code_body.children, None)
                self.assertIsNotNone(cdata_block)
                self.assertTrue(isinstance(cdata_block, CData))

            # blocks should by python by default (per Sphinx)
            for code_macro in code_macros:
                lang = code_macro.find('ac:parameter', {'ac:name': 'language'})
                self.assertIsNotNone(lang)
                self.assertEqual(lang.text, 'python')

    @setup_builder('confluence')
    def test_storage_rst_literal_includes(self):
        out_dir = self.build(self.dataset, filenames=['literal-includes'])

        with parse('literal-includes', out_dir) as data:
            code_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'code'})
            self.assertIsNotNone(code_macros)
            self.assertEqual(len(code_macros), 6)

            # ensure each code block has cdata content
            for code_macro in code_macros:
                code_body = code_macro.find('ac:plain-text-body')
                cdata_block = next(code_body.children, None)
                self.assertIsNotNone(cdata_block)
                self.assertTrue(isinstance(cdata_block, CData))

            # c block
            block = code_macros.pop(0)

            lang = block.find('ac:parameter', {'ac:name': 'language'})
            self.assertIsNotNone(lang)
            self.assertEqual(lang.text, 'cpp')

            linenumbers = block.find('ac:parameter', {'ac:name': 'linenumbers'})
            self.assertIsNotNone(linenumbers)
            self.assertEqual(linenumbers.text, 'false')

            firstline = block.find('ac:parameter', {'ac:name': 'firstline'})
            self.assertIsNone(firstline)

            # cpp block
            block = code_macros.pop(0)

            lang = block.find('ac:parameter', {'ac:name': 'language'})
            self.assertIsNotNone(lang)
            self.assertEqual(lang.text, 'cpp')

            linenumbers = block.find('ac:parameter', {'ac:name': 'linenumbers'})
            self.assertIsNotNone(linenumbers)
            self.assertEqual(linenumbers.text, 'false')

            firstline = block.find('ac:parameter', {'ac:name': 'firstline'})
            self.assertIsNone(firstline)

            # html block
            block = code_macros.pop(0)

            lang = block.find('ac:parameter', {'ac:name': 'language'})
            self.assertIsNotNone(lang)
            self.assertEqual(lang.text, 'html/xml')

            linenumbers = block.find('ac:parameter', {'ac:name': 'linenumbers'})
            self.assertIsNotNone(linenumbers)
            self.assertEqual(linenumbers.text, 'true')

            firstline = block.find('ac:parameter', {'ac:name': 'firstline'})
            self.assertIsNone(firstline)

            # java block
            block = code_macros.pop(0)

            lang = block.find('ac:parameter', {'ac:name': 'language'})
            self.assertIsNotNone(lang)
            self.assertEqual(lang.text, 'java')

            linenumbers = block.find('ac:parameter', {'ac:name': 'linenumbers'})
            self.assertIsNotNone(linenumbers)
            self.assertEqual(linenumbers.text, 'false')

            firstline = block.find('ac:parameter', {'ac:name': 'firstline'})
            self.assertIsNone(firstline)

            # python block
            block = code_macros.pop(0)

            lang = block.find('ac:parameter', {'ac:name': 'language'})
            self.assertIsNotNone(lang)
            self.assertEqual(lang.text, 'python')

            linenumbers = block.find('ac:parameter', {'ac:name': 'linenumbers'})
            self.assertIsNotNone(linenumbers)
            self.assertEqual(linenumbers.text, 'false')

            firstline = block.find('ac:parameter', {'ac:name': 'firstline'})
            self.assertIsNone(firstline)

            # python (lineno-match) block
            block = code_macros.pop(0)

            lang = block.find('ac:parameter', {'ac:name': 'language'})
            self.assertIsNotNone(lang)
            self.assertEqual(lang.text, 'python')

            linenumbers = block.find('ac:parameter', {'ac:name': 'linenumbers'})
            self.assertIsNotNone(linenumbers)
            self.assertEqual(linenumbers.text, 'true')

            firstline = block.find('ac:parameter', {'ac:name': 'firstline'})
            self.assertIsNotNone(firstline)
            self.assertEqual(firstline.text, '6')
