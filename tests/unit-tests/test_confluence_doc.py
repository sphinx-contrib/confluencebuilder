# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinx.errors import SphinxWarning
from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceDoc(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'confluence-doc'

    @setup_builder('html')
    def test_html_confluence_doc_ignore(self):
        # build attempt should not throw an exception/error
        self.build(self.dataset, relax=True)

    @setup_builder('confluence')
    def test_storage_confluence_doc_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            links = data.find_all('ac:link')
            self.assertEqual(len(links), 5)

            # ##########################################################
            # inline card
            # ##########################################################
            link = links.pop(0)

            self.assertTrue(link.has_attr('ac:card-appearance'))
            self.assertEqual(link['ac:card-appearance'], 'inline')

            page_ref = link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'second page')

            # ##########################################################
            # embed card (default)
            # ##########################################################
            link = links.pop(0)

            self.assertTrue(link.has_attr('ac:card-appearance'))
            self.assertEqual(link['ac:card-appearance'], 'embed')

            page_ref = link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'second page')

            # ##########################################################
            # embed card with a width percentage provided
            # ##########################################################
            link = links.pop(0)

            self.assertTrue(link.has_attr('ac:card-appearance'))
            self.assertEqual(link['ac:card-appearance'], 'embed')
            self.assertTrue(link.has_attr('ac:width'))
            self.assertEqual(link['ac:width'], '30')

            page_ref = link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'second page')

            # ##########################################################
            # embed card with a layout provided
            # ##########################################################
            link = links.pop(0)

            self.assertTrue(link.has_attr('ac:card-appearance'))
            self.assertEqual(link['ac:card-appearance'], 'embed')
            self.assertTrue(link.has_attr('ac:layout'))
            self.assertEqual(link['ac:layout'], 'align-end')

            page_ref = link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'second page')

            # ##########################################################
            # block card
            # ##########################################################
            link = links.pop(0)

            self.assertTrue(link.has_attr('ac:card-appearance'))
            self.assertEqual(link['ac:card-appearance'], 'block')

            page_ref = link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'third page')

    @setup_builder('confluence')
    def test_storage_confluence_doc_invalid_doc(self):
        dataset = self.dataset.parent / (self.dataset.name + '-invalid-doc')
        with self.assertRaises(SphinxWarning):
            self.build(dataset)

    @setup_builder('confluence')
    def test_storage_confluence_doc_invalid_layout(self):
        dataset = self.dataset.parent / (self.dataset.name + '-invalid-layout')
        with self.assertRaises(SphinxWarning):
            self.build(dataset)

    @setup_builder('confluence')
    def test_storage_confluence_doc_invalid_width(self):
        dataset = self.dataset.parent / (self.dataset.name + '-invalid-width')
        with self.assertRaises(SphinxWarning):
            self.build(dataset)
