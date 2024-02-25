# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceNewline(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'newline'

    @setup_builder('confluence')
    def test_storage_confluence_newline_directive_expected(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            # expect three tags | p, br, p
            tags = data.find_all()
            self.assertEqual(len(tags), 3)

            para = tags[0]
            self.assertEqual(para.name, 'p')
            self.assertEqual(para.text, 'line1')

            para = tags[1]
            self.assertEqual(para.name, 'br')

            para = tags[2]
            self.assertEqual(para.name, 'p')
            self.assertEqual(para.text, 'line2')
