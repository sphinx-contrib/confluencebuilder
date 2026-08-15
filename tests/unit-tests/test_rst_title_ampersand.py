# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceRstTitleAmpersand(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'title-ampersand'

    @setup_builder('confluence')
    def test_storage_rst_title_ampersand_anchor(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            headers = data.find_all('h2')
            self.assertEqual(len(headers), 2)

            toc_header, section_header = headers
            self.assertEqual(toc_header.text.strip(), 'Contents')

            # heading text itself should render correctly (already escaped
            # properly before this fix)
            self.assertIn('Foo & Bar', section_header.get_text())

            # an anchor macro should still be built for this heading, even
            # though its title contains an ampersand
            anchor_tags = section_header.find_all(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertGreaterEqual(len(anchor_tags), 1)

            for anchor_tag in anchor_tags:
                self.assertIsNotNone(anchor_tag.find('ac:parameter'))

            # the local table-of-contents link should resolve to the same
            # (id-based) anchor target
            toc_link = toc_header.find_next('ac:link')
            self.assertIsNotNone(toc_link)
            self.assertTrue(toc_link.has_attr('ac:anchor'))
            self.assertEqual(toc_link['ac:anchor'], 'foo-bar')
