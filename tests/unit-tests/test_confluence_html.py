# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from bs4 import BeautifulSoup
from bs4 import CData
from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceHtml(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'html'

    @setup_builder('confluence')
    def test_storage_confluence_html_custom_macro(self):
        config = dict(self.config)
        config['confluence_html_macro'] = 'custom-html'
        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            html_macro = data.find('ac:structured-macro',
                {'ac:name': 'custom-html'})
            self.assertIsNotNone(html_macro)

            plain_body = html_macro.find('ac:plain-text-body')
            self.assertIsNotNone(plain_body)

            html_macro_cdata = next(plain_body.children, None)
            self.assertIsNotNone(html_macro_cdata)
            self.assertTrue(isinstance(html_macro_cdata, CData))

            html_macro_data = BeautifulSoup(html_macro_cdata, 'html.parser')

            strong_element = html_macro_data.find('strong')
            self.assertIsNotNone(strong_element)
            text_contents = strong_element.text.strip()
            self.assertIsNotNone(text_contents)
            self.assertTrue('strong text' in text_contents)

    @setup_builder('confluence')
    def test_storage_confluence_html_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            html_macro = data.find('ac:structured-macro', {'ac:name': 'html'})
            self.assertIsNotNone(html_macro)

            plain_body = html_macro.find('ac:plain-text-body')
            self.assertIsNotNone(plain_body)

            html_macro_cdata = next(plain_body.children, None)
            self.assertIsNotNone(html_macro_cdata)
            self.assertTrue(isinstance(html_macro_cdata, CData))

            html_macro_data = BeautifulSoup(html_macro_cdata, 'html.parser')

            strong_element = html_macro_data.find('strong')
            self.assertIsNotNone(strong_element)
            text_contents = strong_element.text.strip()
            self.assertIsNotNone(text_contents)
            self.assertTrue('strong text' in text_contents)
