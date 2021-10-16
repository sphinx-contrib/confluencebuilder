# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceUseCaseNestedRef(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        self.config["root_doc"] = "nested-ref-contents"
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, "datasets", "use-cases")
        self.filenames = [
            "nested-ref-contents",
            "nested-ref-external",
        ]

    def test_usecase_nestedref(self):
        out_dir = build_sphinx(
            self.dataset, config=self.config, filenames=self.filenames
        )

        with parse("nested-ref-contents", out_dir) as data:
            # contents link to header (via anchor)
            root_toc = data.find("ul", recursive=False)
            self.assertIsNotNone(root_toc)

            toc_link = root_toc.find("ac:link")
            self.assertIsNotNone(toc_link)
            self.assertTrue(toc_link.has_attr("ac:anchor"))
            # note: anchor will be `customname` as confluence will strip
            #       underscores in headers with links
            self.assertEqual(toc_link["ac:anchor"], "customname")

            toc_link_body = toc_link.find("ac:link-body", recursive=False)
            self.assertIsNotNone(toc_link_body)
            self.assertEqual(toc_link_body.text, "custom_name")

            # header link to external page
            header = data.find("h2", recursive=False)
            self.assertIsNotNone(header)

            header_link = header.find("ac:link", recursive=False)
            self.assertIsNotNone(header_link)
            self.assertFalse(header_link.has_attr("ac:anchor"))

            header_link_body = header_link.find("ac:link-body", recursive=False)
            self.assertIsNotNone(header_link_body)
            self.assertEqual(header_link_body.text, "custom_name")
