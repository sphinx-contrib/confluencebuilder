# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceSinglepageUniqueReferences(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'contents-multipage'

    @setup_builder('singleconfluence')
    def test_storage_singlepage_unique_references(self):
        """validate single page references are unique (storage)"""
        #
        # Ensure when generating a single page that merged pages produce
        # proper references to their sub-sections.

        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            # verify that all generated anchors are unique
            unique_anchors = set()
            anchor_tags = data.find_all('ac:parameter', {'ac:name': ''})
            for anchor_tag in anchor_tags:
                anchor_id = anchor_tag.text
                self.assertNotIn(anchor_id, unique_anchors)
                unique_anchors.add(anchor_id)

            # verify that each link we have points to a unique anchor
            #
            # Note that will it is possible for documents to have more than
            # one link target a single anchor, for this test, we check for
            # uniqueness to ensure that each local TOC reference is pointing
            # to a specific section title.
            unique_anchor_targets = set()
            link_tags = data.find_all('ac:link')
            for link_tag in link_tags:
                if link_tag.has_attr('ac:anchor'):
                    anchor_id = link_tag['ac:anchor']
                    self.assertNotIn(anchor_id, unique_anchor_targets)
                    unique_anchor_targets.add(anchor_id)
