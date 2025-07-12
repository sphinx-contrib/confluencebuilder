# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


def strval(obj):
    return ''.join(obj.find_all(string=True, recursive=False)).strip()


class TestConfluenceRstHeadings(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'headings'

    @setup_builder('confluence')
    def test_storage_rst_headings_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            header_lvl1 = data.find('h1')
            self.assertIsNone(header_lvl1)

            header_lvl2 = data.find('h2')
            self.assertIsNotNone(header_lvl2)
            self.assertEqual(strval(header_lvl2), 'header 2')

            header_lvl3 = data.find_all('h3')
            self.assertIsNotNone(header_lvl3)
            self.assertEqual(len(header_lvl3), 2)
            self.assertEqual(strval(header_lvl3[0]), 'header 3')
            self.assertEqual(strval(header_lvl3[1]), 'header 12')

            header_lvl4 = data.find('h4')
            self.assertIsNotNone(header_lvl4)
            self.assertEqual(strval(header_lvl4), 'header 4')

            header_lvl5 = data.find('h5')
            self.assertIsNotNone(header_lvl5)
            self.assertEqual(strval(header_lvl5), 'header 5')

            header_lvl6 = data.find_all('h6')
            self.assertIsNotNone(header_lvl6)
            self.assertEqual(len(header_lvl6), 6)

    @setup_builder('confluence')
    def test_storage_rst_headings_with_title(self):
        config = dict(self.config)
        config['confluence_remove_title'] = False

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            header_lvl1 = data.find('h1', recursive=False)
            print(header_lvl1)
            self.assertIsNotNone(header_lvl1)
            self.assertEqual(strval(header_lvl1), 'header 1')

            header_lvl2 = data.find('h2', recursive=False)
            self.assertIsNotNone(header_lvl2)
            self.assertEqual(strval(header_lvl2), 'header 2')

            header_lvl3 = data.find_all('h3', recursive=False)
            self.assertIsNotNone(header_lvl3)
            self.assertEqual(len(header_lvl3), 2)
            self.assertEqual(strval(header_lvl3[0]), 'header 3')
            self.assertEqual(strval(header_lvl3[1]), 'header 12')

            header_lvl4 = data.find('h4', recursive=False)
            self.assertIsNotNone(header_lvl4)
            self.assertEqual(strval(header_lvl4), 'header 4')

            header_lvl5 = data.find('h5', recursive=False)
            self.assertIsNotNone(header_lvl5)
            self.assertEqual(strval(header_lvl5), 'header 5')

            header_lvl6 = data.find_all('h6', recursive=False)
            self.assertIsNotNone(header_lvl6)
            self.assertEqual(len(header_lvl6), 6)
