# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceRstHeadings(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'headings',
        ]

    def test_storage_rst_headings_default(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('headings', out_dir) as data:
            header_lvl1 = data.find('h1')
            self.assertIsNone(header_lvl1)

            header_lvl2 = data.find('h2')
            self.assertIsNotNone(header_lvl2)
            self.assertEqual(header_lvl2.text, 'header 2')

            header_lvl3 = data.find_all('h3')
            self.assertIsNotNone(header_lvl3)
            self.assertEqual(len(header_lvl3), 2)
            self.assertEqual(header_lvl3[0].text, 'header 3')
            self.assertEqual(header_lvl3[1].text, 'header 12')

            header_lvl4 = data.find('h4')
            self.assertIsNotNone(header_lvl4)
            self.assertEqual(header_lvl4.text, 'header 4')

            header_lvl5 = data.find('h5')
            self.assertIsNotNone(header_lvl5)
            self.assertEqual(header_lvl5.text, 'header 5')

            header_lvl6 = data.find_all('h6')
            self.assertIsNotNone(header_lvl6)
            self.assertEqual(len(header_lvl6), 6)

    def test_storage_rst_headings_with_title(self):
        config = dict(self.config)
        config['confluence_remove_title'] = False

        out_dir = build_sphinx(self.dataset, config=config,
            filenames=self.filenames)

        with parse('headings', out_dir) as data:
            header_lvl1 = data.find('h1')
            self.assertIsNotNone(header_lvl1)
            self.assertEqual(header_lvl1.text, 'header 1')

            header_lvl2 = data.find('h2')
            self.assertIsNotNone(header_lvl2)
            self.assertEqual(header_lvl2.text, 'header 2')

            header_lvl3 = data.find_all('h3')
            self.assertIsNotNone(header_lvl3)
            self.assertEqual(len(header_lvl3), 2)
            self.assertEqual(header_lvl3[0].text, 'header 3')
            self.assertEqual(header_lvl3[1].text, 'header 12')

            header_lvl4 = data.find('h4')
            self.assertIsNotNone(header_lvl4)
            self.assertEqual(header_lvl4.text, 'header 4')

            header_lvl5 = data.find('h5')
            self.assertIsNotNone(header_lvl5)
            self.assertEqual(header_lvl5.text, 'header 5')

            header_lvl6 = data.find_all('h6')
            self.assertIsNotNone(header_lvl6)
            self.assertEqual(len(header_lvl6), 6)
