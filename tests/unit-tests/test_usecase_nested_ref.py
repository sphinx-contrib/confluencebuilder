# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceUseCaseNestedRef(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.config['root_doc'] = 'nested-ref-contents'
        cls.dataset = os.path.join(cls.datasets, 'use-cases')
        cls.filenames = [
            'nested-ref-contents',
            'nested-ref-external',
        ]

    @setup_builder('confluence')
    def test_usecase_storage_nestedref(self):
        out_dir = self.build(self.dataset, filenames=self.filenames)

        with parse('nested-ref-contents', out_dir) as data:
            # contents link to header (via anchor)
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            toc_link = root_toc.find('ac:link')
            self.assertIsNotNone(toc_link)
            self.assertTrue(toc_link.has_attr('ac:anchor'))
            self.assertEqual(toc_link['ac:anchor'], 'custom_name')

            toc_link_body = toc_link.find('ac:link-body', recursive=False)
            self.assertIsNotNone(toc_link_body)
            self.assertEqual(toc_link_body.text, 'custom_name')

            # header links
            headers = data.find_all('h2')
            self.assertEqual(len(headers), 3)

            # header link to external page
            header = headers.pop(0)
            self.assertIsNotNone(header)

            header_link = header.find('ac:link', recursive=False)
            self.assertIsNotNone(header_link)
            self.assertFalse(header_link.has_attr('ac:anchor'))

            header_link_body = header_link.find('ac:link-body', recursive=False)
            self.assertIsNotNone(header_link_body)
            self.assertEqual(header_link_body.text, 'custom_name')

            # header link to external page's header
            header = headers.pop(0)
            self.assertIsNotNone(header)

            header_link = header.find('ac:link', recursive=False)
            self.assertIsNotNone(header_link)
            self.assertTrue(header_link.has_attr('ac:anchor'))
            self.assertEqual(header_link['ac:anchor'], 'section')

            header_link_body = header_link.find('ac:link-body', recursive=False)
            self.assertIsNotNone(header_link_body)
            self.assertEqual(header_link_body.text, 'custom_name2')

            # header link to external page's anchor
            header = headers.pop(0)
            self.assertIsNotNone(header)

            header_link = header.find('ac:link', recursive=False)
            self.assertIsNotNone(header_link)
            self.assertTrue(header_link.has_attr('ac:anchor'))
            self.assertEqual(header_link['ac:anchor'], 'ref2')

            header_link_body = header_link.find('ac:link-body', recursive=False)
            self.assertIsNotNone(header_link_body)
            self.assertEqual(header_link_body.text, 'custom_name3')
