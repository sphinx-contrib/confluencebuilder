# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from bs4 import CData

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceSphinxCodeblock(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, "datasets", "common")

    def test_storage_sphinx_codeblock_caption(self):
        out_dir = build_sphinx(
            self.dataset, config=self.config, filenames=["code-block-caption"]
        )

        with parse("code-block-caption", out_dir) as data:
            title_param = data.find("ac:parameter", {"ac:name": "title"})
            self.assertIsNotNone(title_param)
            self.assertEqual(title_param.text, "code caption test")

    def test_storage_sphinx_codeblock_default(self):
        out_dir = build_sphinx(
            self.dataset, config=self.config, filenames=["code-block"]
        )

        with parse("code-block", out_dir) as data:
            code_macros = data.find_all("ac:structured-macro")
            self.assertIsNotNone(code_macros)
            self.assertEqual(len(code_macros), 3)

            for code_macro in code_macros:
                self.assertTrue(code_macro.has_attr("ac:name"))
                self.assertEqual(code_macro["ac:name"], "code")

            # python block
            python_block = code_macros.pop(0)

            python_block_lang = python_block.find(
                "ac:parameter", {"ac:name": "language"}
            )
            self.assertIsNotNone(python_block_lang)
            self.assertEqual(python_block_lang.text, "python")

            python_block_linenumbers = python_block.find(
                "ac:parameter", {"ac:name": "linenumbers"}
            )
            self.assertIsNotNone(python_block_linenumbers)
            self.assertEqual(python_block_linenumbers.text, "true")

            python_block_body = python_block.find("ac:plain-text-body")
            python_block_cdata = next(python_block_body.children, None)
            self.assertIsNotNone(python_block_cdata)
            self.assertTrue(isinstance(python_block_cdata, CData))

            # sql block
            sql_block = code_macros.pop(0)

            sql_block_lang = sql_block.find("ac:parameter", {"ac:name": "language"})
            self.assertIsNotNone(sql_block_lang)
            self.assertEqual(sql_block_lang.text, "sql")

            sql_block_linenumbers = sql_block.find(
                "ac:parameter", {"ac:name": "linenumbers"}
            )
            self.assertIsNotNone(sql_block_linenumbers)
            self.assertEqual(sql_block_linenumbers.text, "false")

            sql_block_body = sql_block.find("ac:plain-text-body")
            sql_block_cdata = next(sql_block_body.children, None)
            self.assertIsNotNone(sql_block_cdata)
            self.assertTrue(isinstance(sql_block_cdata, CData))

            # ruby block
            ruby_block = code_macros.pop(0)

            ruby_block_lang = ruby_block.find("ac:parameter", {"ac:name": "language"})
            self.assertIsNotNone(ruby_block_lang)
            self.assertEqual(ruby_block_lang.text, "ruby")

            ruby_block_linenumbers = ruby_block.find(
                "ac:parameter", {"ac:name": "linenumbers"}
            )
            self.assertIsNotNone(ruby_block_linenumbers)
            self.assertEqual(ruby_block_linenumbers.text, "false")

            ruby_block_body = ruby_block.find("ac:plain-text-body")
            ruby_block_cdata = next(ruby_block_body.children, None)
            self.assertIsNotNone(ruby_block_cdata)
            self.assertTrue(isinstance(ruby_block_cdata, CData))

            # (check at least one code block's content)
            self.assertEqual(ruby_block_cdata, "puts 'this is a print statement!'")
