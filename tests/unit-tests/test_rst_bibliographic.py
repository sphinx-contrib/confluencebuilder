# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceRstBibliographic(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'bibliographic'

    @setup_builder('confluence')
    def test_storage_rst_bibliographic_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
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
