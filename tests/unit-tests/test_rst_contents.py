# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import re


class TestConfluenceRstContents(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'contents'

        cls.expected_header_text = [
            'section',
            'subsection',
            'toc',
            'subsubsection',
            'newsection',
        ]

    @setup_builder('confluence')
    def test_storage_rst_contents_backlinks_entry(self):
        expected_header_text = self.expected_header_text[:]

        out_dir = self.build(self.dataset,
            filenames=['contents-backlinks-entry'])

        with parse('contents-backlinks-entry', out_dir) as data:
            # ensure headers link to each entry
            headers = data.find_all(re.compile('^h[1-6]$'))
            self.assertEqual(len(headers), 5)

            for header, expected in zip(headers, expected_header_text):
                if expected == 'toc':
                    continue

                header_link = header.find('ac:link')
                self.assertIsNotNone(header_link)
                self.assertTrue(header_link.has_attr('ac:anchor'))
                self.assertNotEqual(header_link['ac:anchor'], 'toc')

                link_body = header_link.find('ac:link-body', recursive=False)
                self.assertIsNotNone(link_body)
                self.assertEqual(link_body.text, expected)

    @setup_builder('confluence')
    def test_storage_rst_contents_backlinks_none(self):
        expected_header_text = self.expected_header_text[:]

        out_dir = self.build(self.dataset,
            filenames=['contents-backlinks-none'])

        with parse('contents-backlinks-none', out_dir) as data:
            # ensure headers are not links
            headers = data.find_all(re.compile('^h[1-6]$'))
            self.assertEqual(len(headers), 5)

            for header, expected in zip(headers, expected_header_text):
                txt = ''.join(
                    header.find_all(string=True, recursive=False)).strip()
                self.assertEqual(txt, expected)

    @setup_builder('confluence')
    def test_storage_rst_contents_backlinks_top(self):
        expected_header_text = self.expected_header_text[:]

        out_dir = self.build(self.dataset,
            filenames=['contents-backlinks-top'])

        with parse('contents-backlinks-top', out_dir) as data:
            # ensure headers link to top
            headers = data.find_all(re.compile('^h[1-6]$'))
            self.assertEqual(len(headers), 5)

            for header, expected in zip(headers, expected_header_text):
                if expected == 'toc':
                    continue

                header_link = header.find('ac:link')
                self.assertIsNotNone(header_link)
                self.assertTrue(header_link.has_attr('ac:anchor'))
                self.assertEqual(header_link['ac:anchor'], 'toc')  # fixed

                link_body = header_link.find('ac:link-body', recursive=False)
                self.assertIsNotNone(link_body)
                self.assertEqual(link_body.text, expected)

    @setup_builder('confluence')
    def test_storage_rst_contents_caption(self):
        out_dir = self.build(self.dataset, filenames=['contents-caption'])

        with parse('contents-caption', out_dir) as data:
            caption = data.find(re.compile('^h[1-6]$'),
                text='table of contents')
            self.assertIsNotNone(caption)

    @setup_builder('confluence')
    def test_storage_rst_contents_default_title(self):
        config = dict(self.config)
        config['confluence_remove_title'] = False

        out_dir = self.build(self.dataset, config=config,
            filenames=['contents'])

        with parse('contents', out_dir) as data:
            # there should be no #top link for the contents page
            root_link = data.find('a')
            self.assertIsNone(root_link)

            # find document link (which should be a ac-link reference)
            root_link = data.find('ac:link', attrs={'ac:anchor': 'contents'})
            self.assertIsNotNone(root_link)

            link_body = root_link.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'contents')

    @setup_builder('confluence')
    def test_storage_rst_contents_default_top(self):
        out_dir = self.build(self.dataset, filenames=['contents'])

        with parse('contents', out_dir) as data:
            # there should be no ac-link for the contents page
            root_link = data.find('ac:link', attrs={'ac:anchor': 'contents'})
            self.assertIsNone(root_link)

            # find document link (which should be a #top reference)
            root_link = data.find('a')
            self.assertIsNotNone(root_link)
            self.assertTrue(root_link.has_attr('href'))
            self.assertEqual(root_link['href'], '#top')
            self.assertEqual(root_link.text, 'contents')

    @setup_builder('confluence')
    def test_storage_rst_contents_links(self):
        expected_header_text = self.expected_header_text[:]
        expected_header_text.remove('toc')  # skip toc header

        out_dir = self.build(self.dataset, filenames=['contents'])

        with parse('contents', out_dir) as data:
            toc = data.find('ul')
            self.assertIsNotNone(toc)

            # verify contents link to search sections
            links = toc.find_all('ac:link')
            self.assertEqual(len(links), 4)

            for link, expected in zip(links, expected_header_text):
                self.assertTrue(link.has_attr('ac:anchor'))
                self.assertEqual(link['ac:anchor'], expected)

                link_body = link.find('ac:link-body', recursive=False)
                self.assertIsNotNone(link_body)
                self.assertEqual(link_body.text, expected)

    @setup_builder('confluence')
    def test_storage_rst_contents_local(self):
        out_dir = self.build(self.dataset, filenames=['contents-local'])

        with parse('contents-local', out_dir) as data:
            toc = data.find('ul')
            self.assertIsNotNone(toc)

            links = toc.find_all('ac:link')
            self.assertEqual(len(links), 1)

            link = links[0]
            self.assertTrue(link.has_attr('ac:anchor'))
            self.assertEqual(link['ac:anchor'], 'subsubsection')

            link_body = link.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'subsubsection')
