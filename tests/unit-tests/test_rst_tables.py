# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceRstTables(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'tables',
        ]

    def test_storage_rst_tables_defaults(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('tables', out_dir) as data:
            tables = data.find_all('table', recursive=False)
            self.assertEqual(len(tables), 3)

            # ##########################################################
            # spanning table
            # ##########################################################
            table = tables.pop(0)

            #  (header)
            thead = table.find('thead', recursive=False)
            self.assertIsNotNone(thead)

            trs = thead.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 1)

            tr01 = trs[0]
            ths = tr01.find_all('th', recursive=False)
            self.assertEqual(len(ths), 4)

            expected_contents = [
                '00',
                '01',
                '02',
                '03',
            ]

            for th, expected in zip(ths, expected_contents):
                self.assertEqual(th.text.strip(), expected)

            tds = tr01.find_all('tds', recursive=False)
            self.assertEqual(len(tds), 0)

            #  (body)
            tbody = table.find('tbody', recursive=False)
            self.assertIsNotNone(tbody)

            trs = tbody.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 4)

            #   (row 01 contents check)
            row01 = trs.pop(0)

            tds = row01.find_all('td', recursive=False)
            self.assertEqual(len(tds), 4)

            expected_contents = [
                '10',
                '11',
                '12',
                '13',
            ]

            for th, expected in zip(tds, expected_contents):
                self.assertEqual(th.text.strip(), expected)

            #   (row 02 contents check)
            row02 = trs.pop(0)

            tds = row02.find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            self.assertEqual(tds[0].text.strip(), '20')
            self.assertTrue(tds[1].has_attr('colspan'))
            self.assertEqual(tds[1]['colspan'], '3')
            self.assertEqual(tds[1].text.strip(), '2[1-3]')

            #   (row 03 contents check)
            row03 = trs.pop(0)

            tds = row03.find_all('td', recursive=False)
            self.assertEqual(len(tds), 3)

            self.assertEqual(tds[0].text.strip(), '30')
            self.assertTrue(tds[1].has_attr('rowspan'))
            self.assertEqual(tds[1]['rowspan'], '2')
            self.assertEqual(tds[1].text.strip(), 'ZZ')
            self.assertTrue(tds[2].has_attr('colspan'))
            self.assertEqual(tds[2]['colspan'], '2')
            self.assertTrue(tds[2].has_attr('rowspan'))
            self.assertEqual(tds[2]['rowspan'], '2')
            list_inside_cell = tds[2].find('ul', recursive=False)
            self.assertIsNotNone(list_inside_cell)

            #   (row 04 contents check)
            row04 = trs.pop(0)

            tds = row04.find_all('td', recursive=False)
            self.assertEqual(len(tds), 1)

            self.assertEqual(tds[0].text.strip(), '40')

            # ##########################################################
            # multi-header table
            # ##########################################################
            table = tables.pop(0)

            #  (header)
            thead = table.find('thead', recursive=False)
            self.assertIsNotNone(thead)

            trs = thead.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 2)

            ths = trs[0].find_all('th', recursive=False)
            self.assertEqual(len(ths), 3)

            expected_contents = [
                'a1',
                'a2',
                'a3',
            ]

            for th, expected in zip(ths, expected_contents):
                self.assertEqual(th.text.strip(), expected)

            ths = trs[1].find_all('th', recursive=False)
            self.assertEqual(len(ths), 3)

            expected_contents = [
                'b1',
                'b2',
                'b3',
            ]

            for th, expected in zip(ths, expected_contents):
                self.assertEqual(th.text.strip(), expected)

            #  (body)
            tbody = table.find('tbody', recursive=False)
            self.assertIsNotNone(tbody)

            trs = tbody.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 2)

            tds = trs[0].find_all('td', recursive=False)
            self.assertEqual(len(tds), 3)

            expected_contents = [
                'c1',
                'c2',
                'c3',
            ]

            for td, expected in zip(tds, expected_contents):
                self.assertEqual(td.text.strip(), expected)

            tds = trs[1].find_all('td', recursive=False)
            self.assertEqual(len(tds), 3)

            expected_contents = [
                'd1',
                'd2',
                'd3',
            ]

            for td, expected in zip(tds, expected_contents):
                self.assertEqual(td.text.strip(), expected)

            # ##########################################################
            # nested table
            # ##########################################################
            table = tables.pop(0)

            # (header)
            thead = table.find('thead', recursive=False)
            self.assertIsNotNone(thead)

            trs = thead.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 1)

            ths = trs[0].find_all('th', recursive=False)
            self.assertEqual(len(ths), 2)

            expected_contents = [
                'cell 1',
                'cell 2',
            ]

            for th, expected in zip(ths, expected_contents):
                self.assertEqual(th.text.strip(), expected)

            # (body)
            tbody = table.find('tbody', recursive=False)
            self.assertIsNotNone(tbody)

            trs = tbody.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 1)

            tds = trs[0].find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            self.assertEqual(tds[0].text.strip(), 'cell 3')

            rich_cell = tds[1]
            rich_cell_leading = rich_cell.find('p', recursive=False)
            self.assertIsNotNone(rich_cell_leading)
            self.assertEqual(rich_cell_leading.text, 'cell 4')

            # ##########################################################
            # nested table (internal)
            # ##########################################################
            nested_table = rich_cell.find('table', recursive=False)

            # (header)
            thead = nested_table.find('thead', recursive=False)
            self.assertIsNotNone(thead)

            trs = thead.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 1)

            ths = trs[0].find_all('th', recursive=False)
            self.assertEqual(len(ths), 2)

            expected_contents = [
                'a',
                'b',
            ]

            for th, expected in zip(ths, expected_contents):
                self.assertEqual(th.text.strip(), expected)

            #  (body)
            tbody = nested_table.find('tbody', recursive=False)
            self.assertIsNotNone(tbody)

            trs = tbody.find_all('tr', recursive=False)
            self.assertEqual(len(trs), 2)

            tds = trs[0].find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            expected_contents = [
                'c',
                'd',
            ]

            for td, expected in zip(tds, expected_contents):
                self.assertEqual(td.text.strip(), expected)

            tds = trs[1].find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            expected_contents = [
                'e',
                'f',
            ]

            for td, expected in zip(tds, expected_contents):
                self.assertEqual(td.text.strip(), expected)
