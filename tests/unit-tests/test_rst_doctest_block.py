# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from bs4 import CData
from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceRstDoctestBlock(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'doctest-block'

    @setup_builder('confluence')
    def test_storage_rst_doctest_block(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            code_macros = data.find_all('ac:structured-macro')
            self.assertIsNotNone(code_macros)
            self.assertEqual(len(code_macros), 1)

            for code_macro in code_macros:
                self.assertTrue(code_macro.has_attr('ac:name'))
                self.assertEqual(code_macro['ac:name'], 'code')

            doctest_block = code_macros.pop(0)

            doctest_block_lang = doctest_block.find('ac:parameter',
                {'ac:name': 'language'})
            self.assertIsNotNone(doctest_block_lang)
            self.assertEqual(doctest_block_lang.text, 'python')

            doctest_block_body = doctest_block.find('ac:plain-text-body')
            doctest_block_cdata = next(doctest_block_body.children, None)
            self.assertIsNotNone(doctest_block_cdata)
            self.assertTrue(isinstance(doctest_block_cdata, CData))
