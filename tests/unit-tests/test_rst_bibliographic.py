# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceRstBibliographic(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'bibliographic',
        ]

    def test_storage_rst_bibliographic_defaults(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('bibliographic', out_dir) as data:
            biblio_table = data.find('table')
            self.assertIsNotNone(biblio_table)

            rows = biblio_table.find_all('tr')
            self.assertIsNotNone(rows)

            for row in rows:
                cols = row.find_all('td')
                self.assertIsNotNone(cols)
                self.assertEqual(len(cols), 2)

                field_title = cols[0].find('strong', recursive=False)
                self.assertIsNotNone(field_title)
                self.assertIsNotNone(field_title.contents)

                self.assertIsNotNone(cols[1].contents)
