# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinx.errors import SphinxWarning
from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceLink(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'confluence-link'

    @setup_builder('html')
    def test_html_confluence_link_ignore(self):
        # build attempt should not throw an exception/error
        self.build(self.dataset, relax=True)

    @setup_builder('confluence')
    def test_storage_confluence_link_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            links = data.find_all('a')
            self.assertEqual(len(links), 5)

            # ##########################################################
            # inline card
            # ##########################################################
            link = links.pop(0)

            self.assertTrue(link.has_attr('data-card-appearance'))
            self.assertEqual(link['data-card-appearance'], 'inline')
            self.assertTrue(link.has_attr('href'))
            self.assertEqual(link['href'], 'https://example.com')

            # ##########################################################
            # embed card (default)
            # ##########################################################
            link = links.pop(0)

            self.assertTrue(link.has_attr('data-card-appearance'))
            self.assertEqual(link['data-card-appearance'], 'embed')
            self.assertTrue(link.has_attr('href'))
            self.assertEqual(link['href'], 'https://www.example.org')

            # ##########################################################
            # embed card with a width percentage provided
            # ##########################################################
            link = links.pop(0)

            self.assertTrue(link.has_attr('data-card-appearance'))
            self.assertEqual(link['data-card-appearance'], 'embed')
            self.assertTrue(link.has_attr('href'))
            self.assertEqual(link['href'], 'https://example.com')
            self.assertTrue(link.has_attr('data-width'))
            self.assertEqual(link['data-width'], '80')

            # ##########################################################
            # embed card with a layout provided
            # ##########################################################
            link = links.pop(0)

            self.assertTrue(link.has_attr('data-card-appearance'))
            self.assertEqual(link['data-card-appearance'], 'embed')
            self.assertTrue(link.has_attr('href'))
            self.assertEqual(link['href'], 'https://example.org')
            self.assertTrue(link.has_attr('data-layout'))
            self.assertEqual(link['data-layout'], 'align-end')

            # ##########################################################
            # block card
            # ##########################################################
            link = links.pop(0)

            self.assertTrue(link.has_attr('data-card-appearance'))
            self.assertEqual(link['data-card-appearance'], 'block')
            self.assertTrue(link.has_attr('href'))
            self.assertEqual(link['href'], 'https://www.example.com')

    @setup_builder('confluence')
    def test_storage_confluence_link_invalid_layout(self):
        dataset = self.dataset.parent / (self.dataset.name + '-invalid-layout')
        with self.assertRaises(SphinxWarning):
            self.build(dataset)

    @setup_builder('confluence')
    def test_storage_confluence_link_invalid_width(self):
        dataset = self.dataset.parent / (self.dataset.name + '-invalid-width')
        with self.assertRaises(SphinxWarning):
            self.build(dataset)
