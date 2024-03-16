# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceLocalToc(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'local-toc'

    @setup_builder('confluence')
    def test_storage_local_toc(self):
        out_dir = self.build(self.dataset)

        with parse('rst-v1', out_dir) as data:
            # for v1, no a-tags
            a_tags = data.find_all('a')
            self.assertEqual(len(a_tags), 0)

            # for v2, expect two ac:links:
            #  - link to section
            #  - link to toc section entry
            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 2)

            # (ac-link 1) link to section
            #
            # This check is important since v2 links will have anchors with
            # no separators.
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'AnExtraHeader')

            # (ac-link 2) link to toc section entry
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertNotEqual(ac_link['ac:anchor'], '')

        with parse('rst-v2', out_dir) as data:
            # for v1, one a tag linked to section
            a_tags = data.find_all('a')
            self.assertEqual(len(a_tags), 1)

            # (a 1) link to section
            #
            # This check is important since v2 links will have anchors with
            # dashes for separators.
            a_tag = a_tags.pop(0)
            self.assertTrue(a_tag.has_attr('href'))
            self.assertEqual(a_tag['href'], '#An-Extra-Header')

            # for v2, one ac:links linked to toc section entry
            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 1)

            # (ac-link 1) link to toc section entry
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertNotEqual(ac_link['ac:anchor'], '')
