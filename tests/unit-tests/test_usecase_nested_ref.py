# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest

class TestConfluenceUseCaseNestedRef(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        self.config['root_doc'] = 'nested-ref-contents'
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'use-cases')
        self.filenames = [
            'nested-ref-contents',
            'nested-ref-external',
        ]

    def test_usecase_nestedref(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

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
