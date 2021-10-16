# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import re
import unittest

from sphinxcontrib.confluencebuilder.state import ConfluenceState
from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceConfigPrevNext(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        self.config["confluence_max_doc_depth"] = 1
        self.config["confluence_page_hierarchy"] = True

        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, "datasets", "hierarchy")

    def test_config_hierarchy_max_depth(self):
        out_dir = build_sphinx(self.dataset, config=self.config, relax=True)

        index = os.path.join(out_dir, "index.conf")
        self.assertTrue(
            os.path.exists(index), "expected file was not generated: {}".format(index)
        )

        # ensure no documents are created beyond the maximum depth
        test_paths = [
            os.path.join(out_dir, "toctree-doc2a.conf"),
            os.path.join(out_dir, "toctree-doc2aa.conf"),
            os.path.join(out_dir, "toctree-doc2aaa.conf"),
            os.path.join(out_dir, "toctree-doc2b.conf"),
            os.path.join(out_dir, "toctree-doc2c.conf"),
        ]
        for test_path in test_paths:
            self.assertFalse(
                os.path.exists(test_path),
                "unexpected file was generated: {}".format(test_path),
            )

    def test_config_hierarchy_parent_registration(self):
        ConfluenceState.reset()
        build_sphinx(self.dataset, config=self.config, relax=True)

        # root toctree should not have a parent
        root_doc = ConfluenceState.parentDocname("index")
        self.assertIsNone(root_doc)

        # check various documents for expected parents
        parent_doc = ConfluenceState.parentDocname("toctree-doc1")
        self.assertEqual(parent_doc, "index")

        parent_doc = ConfluenceState.parentDocname("toctree-doc2")
        self.assertEqual(parent_doc, "index")

        parent_doc = ConfluenceState.parentDocname("toctree-doc3")
        self.assertEqual(parent_doc, "index")

        parent_doc = ConfluenceState.parentDocname("toctree-doc2a")
        self.assertEqual(parent_doc, "toctree-doc2")

    def test_storage_config_hierarchy_max_depth(self):
        out_dir = build_sphinx(self.dataset, config=self.config, relax=True)

        # ensure data is merged in when capping the depth
        doc2_expected_headers = [
            "treedoc2a",
            "hyperlink references (part a)",
            "treedoc2aa",
            "treedoc2aaa",
            "treedoc2b",
            "treedoc2c",
            "check citations",
            "hyperlink references (part b)",
        ]

        with parse("toctree-doc1", out_dir) as data:
            # sanity check anchor creation
            anchor_tag = data.find("ac:structured-macro")
            self.assertIsNotNone(anchor_tag)
            self.assertTrue(anchor_tag.has_attr("ac:name"))
            self.assertEqual(anchor_tag["ac:name"], "anchor")

            anchor_param = anchor_tag.find("ac:parameter", recursive=False)
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, "example-doc1-label")

            # ensure link back to combined doc2 page
            link_tag = data.find("ac:link")
            self.assertIsNotNone(link_tag)

            self.assertTrue(link_tag.has_attr("ac:anchor"))
            self.assertEqual(link_tag["ac:anchor"], "checkcitations")

            page_ref = link_tag.find("ri:page")
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref["ri:content-title"], "treedoc2")

            link_body = link_tag.find("ac:link-body", recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, "doc2c")

        with parse("toctree-doc2", out_dir) as data:
            # ensure headers in the "two" group have all been merged in
            headers = data.find_all(re.compile("^h[1-6]$"))
            self.assertEqual(len(headers), len(doc2_expected_headers))

            for header, expected in zip(headers, doc2_expected_headers):
                self.assertEqual(header.text, expected)

            # check if links are pointing to other documents
            link_tags = data.find_all("ac:link")
            self.assertIsNotNone(link_tags)

            doc1_link_tag = link_tags.pop(0)
            self.assertTrue(doc1_link_tag.has_attr("ac:anchor"))
            self.assertEqual(doc1_link_tag["ac:anchor"], "example-doc1-label")

            doc1_page_ref = doc1_link_tag.find("ri:page")
            self.assertIsNotNone(doc1_page_ref)
            self.assertEqual(doc1_page_ref["ri:content-title"], "treedoc1")

            doc1_link_body = doc1_link_tag.find("ac:link-body", recursive=False)
            self.assertIsNotNone(doc1_link_body)
            self.assertEqual(doc1_link_body.text, "doc1")

            doc2_link_tag = link_tags.pop(0)
            self.assertTrue(doc2_link_tag.has_attr("ac:anchor"))
            self.assertEqual(doc2_link_tag["ac:anchor"], "example-doc3-label")

            doc2_page_ref = doc2_link_tag.find("ri:page")
            self.assertIsNotNone(doc2_page_ref)
            self.assertEqual(doc2_page_ref["ri:content-title"], "treedoc3")

            doc2_link_body = doc2_link_tag.find("ac:link-body", recursive=False)
            self.assertIsNotNone(doc2_link_body)
            self.assertEqual(doc2_link_body.text, "doc2")

        with parse("toctree-doc3", out_dir) as data:
            # sanity check anchor creation
            anchor_tag = data.find("ac:structured-macro")
            self.assertIsNotNone(anchor_tag)
            self.assertTrue(anchor_tag.has_attr("ac:name"))
            self.assertEqual(anchor_tag["ac:name"], "anchor")

            anchor_param = anchor_tag.find("ac:parameter", recursive=False)
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, "example-doc3-label")

            # ensure link back to combined doc2 page
            link_tag = data.find("ac:link")
            self.assertIsNotNone(link_tag)

            self.assertTrue(link_tag.has_attr("ac:anchor"))
            self.assertEqual(link_tag["ac:anchor"], "hyperlinkreferences(parta)")

            page_ref = link_tag.find("ri:page")
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref["ri:content-title"], "treedoc2")

            link_body = link_tag.find("ac:link-body", recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, "doc2a")
