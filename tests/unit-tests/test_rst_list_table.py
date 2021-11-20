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


class TestConfluenceRstListTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'common')
        cls.filenames = [
            'list-table',
        ]

    def test_storage_rst_listtable(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('list-table', out_dir) as data:
            root_tags = data.find_all(recursive=False)
            self.assertEqual(len(root_tags), 6)

            # ##########################################################
            # table 1 (basic)
            # ##########################################################
            label = root_tags.pop(0)
            stronged_label = label.find('strong')
            self.assertIsNotNone(stronged_label)
            self.assertEqual(stronged_label.text, 'name1')

            table = root_tags.pop(0)

            #  (header)
            thead = table.find('thead', recursive=False)
            self.assertIsNotNone(thead)

            trs = thead.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 1)

            tr01 = trs[0]
            ths = tr01.find_all('th', recursive=False)
            self.assertEqual(len(ths), 2)

            expected_contents = [
                'key',
                'value',
            ]

            for th, expected in zip(ths, expected_contents):
                self.assertEqual(th.text.strip(), expected)

            tds = tr01.find_all('tds', recursive=False)
            self.assertEqual(len(tds), 0)

            #  (body)
            tbody = table.find('tbody', recursive=False)
            self.assertIsNotNone(tbody)

            trs = tbody.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 2)

            #   (row 01 contents check)
            row01 = trs.pop(0)

            tds = row01.find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            expected_contents = [
                '1',
                '2',
            ]

            for td, expected in zip(tds, expected_contents):
                self.assertEqual(td.text.strip(), expected)

            #   (row 02 contents check)
            row02 = trs.pop(0)

            tds = row02.find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            expected_contents = [
                '3',
                '4',
            ]

            for td, expected in zip(tds, expected_contents):
                self.assertEqual(td.text.strip(), expected)

            # ##########################################################
            # table 2 (two headers)
            # ##########################################################
            label = root_tags.pop(0)
            stronged_label = label.find('strong')
            self.assertIsNotNone(stronged_label)
            self.assertEqual(stronged_label.text, 'name2')

            table = root_tags.pop(0)

            #  (header)
            thead = table.find('thead', recursive=False)
            self.assertIsNotNone(thead)

            trs = thead.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 2)

            #   (header 01 contents check)
            header01 = trs.pop(0)

            ths = header01.find_all('th', recursive=False)
            self.assertEqual(len(ths), 3)

            expected_contents = [
                'key1',
                'value1',
                'description1',
            ]

            for th, expected in zip(ths, expected_contents):
                self.assertEqual(th.text.strip(), expected)

            #   (header 02 contents check)
            header02 = trs.pop(0)

            ths = header02.find_all('th', recursive=False)
            self.assertEqual(len(ths), 3)

            expected_contents = [
                'key2',
                'value2',
                'description2',
            ]

            for th, expected in zip(ths, expected_contents):
                self.assertEqual(th.text.strip(), expected)

            #  (body)
            tbody = table.find('tbody', recursive=False)
            self.assertIsNotNone(tbody)

            trs = tbody.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 2)

            #   (row 01 contents check)
            row01 = trs.pop(0)

            tds = row01.find_all('td', recursive=False)
            self.assertEqual(len(tds), 3)

            expected_contents = [
                '1',
                '2',
                '3',
            ]

            for td, expected in zip(tds, expected_contents):
                self.assertEqual(td.text.strip(), expected)

            #   (row 02 contents check)
            row02 = trs.pop(0)

            tds = row02.find_all('td', recursive=False)
            self.assertEqual(len(tds), 3)

            expected_contents = [
                '4',
                '5',
                '6',
            ]

            for td, expected in zip(tds, expected_contents):
                self.assertEqual(td.text.strip(), expected)

            # ##########################################################
            # table 3 (stub header)
            # ##########################################################
            label = root_tags.pop(0)
            stronged_label = label.find('strong')
            self.assertIsNotNone(stronged_label)
            self.assertEqual(stronged_label.text, 'name3')

            table = root_tags.pop(0)

            #  (header)
            thead = table.find('thead', recursive=False)
            self.assertIsNotNone(thead)

            trs = thead.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 1)

            tr01 = trs[0]
            ths = tr01.find_all('th', recursive=False)
            self.assertEqual(len(ths), 2)

            expected_contents = [
                'key',
                'value',
            ]

            for th, expected in zip(ths, expected_contents):
                self.assertEqual(th.text.strip(), expected)

            tds = tr01.find_all('tds', recursive=False)
            self.assertEqual(len(tds), 0)

            #  (body)
            tbody = table.find('tbody', recursive=False)
            self.assertIsNotNone(tbody)

            trs = tbody.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 2)

            #   (row 01 contents check)
            row01 = trs.pop(0)

            stub_header = row01.find('th')
            self.assertIsNotNone(stub_header)
            self.assertEqual(stub_header.text.strip(), 'a')

            col_data = row01.find('td')
            self.assertIsNotNone(col_data)
            self.assertEqual(col_data.text.strip(), '4')

            #   (row 02 contents check)
            row02 = trs.pop(0)

            stub_header = row02.find('th')
            self.assertIsNotNone(stub_header)
            self.assertEqual(stub_header.text.strip(), 'b')

            col_data = row02.find('td')
            self.assertIsNotNone(col_data)
            self.assertEqual(col_data.text.strip(), '8')
