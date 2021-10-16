# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceRstBlockQuotes(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, "datasets", "common")
        self.filenames = [
            "block-quotes",
        ]

    def test_storage_rst_block_quotes(self):
        out_dir = build_sphinx(
            self.dataset, config=self.config, filenames=self.filenames
        )

        css_margin_indent = "margin-left: 30px"

        with parse("block-quotes", out_dir) as data:
            div_tags = data.find_all("div")

            # ensure each div element in this example is indented
            for div in div_tags:
                self.assertTrue(div.has_attr("style"))
                self.assertTrue(css_margin_indent in div["style"])
