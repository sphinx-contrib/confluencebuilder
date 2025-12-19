# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib.testcase import setup_editor


class TestConfluenceConfigHeaderFooter(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'pull-quote'

    @setup_builder('confluence')
    def test_storage_rst_pull_quote_v1(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            quotes = data.find_all('div')
            self.assertEqual(len(quotes), 2)

            quote = quotes.pop(0)

            quote_text = quote.find('p')
            self.assertIsNotNone(quote_text)
            self.assertEqual(quote_text.text.strip(), 'quote1')

            quote_sep = quote.find('br')
            self.assertIsNone(quote_sep)

            quote = quotes.pop(0)

            quote_text = quote.find('p')
            self.assertIsNotNone(quote_text)
            self.assertEqual(quote_text.text.strip(), 'quote2')

            quote_sep = quote.find('br')
            self.assertIsNotNone(quote_sep)

            quote_source = quote_sep.next_sibling.strip()
            self.assertEqual(quote_source, '— source')

    @setup_builder('confluence')
    @setup_editor('v2')
    def test_storage_rst_pull_quote_v2(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            quotes = data.find_all('blockquote')
            self.assertEqual(len(quotes), 2)

            quote = quotes.pop(0)

            quote_text = quote.find('p')
            self.assertIsNotNone(quote_text)
            self.assertEqual(quote_text.text.strip(), 'quote1')

            quote = quotes.pop(0)

            quote_text = quote.find('p')
            self.assertIsNotNone(quote_text)
            self.assertEqual(quote_text.text.strip(), 'quote2')

            quote_source = quote_text.next_sibling.strip()
            self.assertEqual(quote_source, '— source')
