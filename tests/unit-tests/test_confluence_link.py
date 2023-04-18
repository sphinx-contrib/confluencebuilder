# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceLink(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'confluence-link')

    @setup_builder('html')
    def test_html_confluence_status_role_ignore(self):
        # build attempt should not throw an exception/error
        self.build(self.dataset, relax=True)

    @setup_builder('confluence')
    def test_storage_confluence_link_role_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            links = data.find_all('a')
            self.assertEqual(len(links), 4)

            # ##########################################################
            # flavour = url
            # ##########################################################
            link = links.pop(0)

            self.assertEqual(link["data-card-appearance"], 'url')

            # ##########################################################
            # flavour = inline
            # ##########################################################
            link = links.pop(0)

            self.assertEqual(link["data-card-appearance"], 'inline')

            # ##########################################################
            # flavour = card
            # ##########################################################
            link = links.pop(0)

            self.assertEqual(link["data-card-appearance"], 'card')

            # ##########################################################
            # flavour = embed
            # ##########################################################
            link = links.pop(0)

            self.assertEqual(link["data-card-appearance"], 'embed')
