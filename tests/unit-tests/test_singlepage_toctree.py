# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2016-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceSinglepageToctree(ConfluenceTestCase):
    @setup_builder('singleconfluence')
    def test_storage_singlepage_toctree_default(self):
        dataset = os.path.join(self.datasets, 'toctree-default')

        out_dir = self.build(dataset)

        with parse('index', out_dir) as data:
            tags = data.find_all()
            self.assertIsNotNone(tags)
            self.assertEqual(len(tags), 12)

            # doc-a content
            doc_a_header = tags.pop(0)
            self.assertEqual(doc_a_header.name, 'h2')
            self.assertEqual(doc_a_header.text, 'doc-a')

            doc_a1_header = tags.pop(0)
            self.assertEqual(doc_a1_header.name, 'h3')
            self.assertEqual(doc_a1_header.text, 'doc-a1')

            content_a1 = tags.pop(0)
            self.assertEqual(content_a1.name, 'p')
            self.assertEqual(content_a1.text, 'content a1')

            doc_a2_header = tags.pop(0)
            self.assertEqual(doc_a2_header.name, 'h3')
            self.assertEqual(doc_a2_header.text, 'doc-a2')

            content_a2 = tags.pop(0)
            self.assertEqual(content_a2.name, 'p')
            self.assertEqual(content_a2.text, 'content a2')

            link_containers = tags.pop(0)
            self.assertEqual(link_containers.name, 'p')

            # (link should be converted into a local anchor)
            link = tags.pop(0)
            self.assertEqual(link.name, 'ac:link')
            self.assertTrue(link.has_attr('ac:anchor'))
            self.assertEqual(link['ac:anchor'], 'doc-b1')

            link_body = tags.pop(0)
            self.assertEqual(link_body.name, 'ac:link-body')
            self.assertEqual(link_body.text, 'custom doc')

            # doc-b content
            doc_b_header = tags.pop(0)
            self.assertEqual(doc_b_header.name, 'h2')
            self.assertEqual(doc_b_header.text, 'doc-b')

            subheader_header = tags.pop(0)
            self.assertEqual(subheader_header.name, 'h3')
            self.assertEqual(subheader_header.text, 'subheader')

            doc_b1_header = tags.pop(0)
            self.assertEqual(doc_b1_header.name, 'h4')
            self.assertEqual(doc_b1_header.text, 'doc-b1')

            content = tags.pop(0)
            self.assertEqual(content.name, 'p')
            self.assertEqual(content.text, 'content b1')

    @setup_builder('singleconfluence')
    def test_storage_singlepage_toctree_numbered(self):
        dataset = os.path.join(self.datasets, 'toctree-numbered')

        out_dir = self.build(dataset)

        with parse('index', out_dir) as data:
            tags = data.find_all()
            self.assertIsNotNone(tags)
            self.assertEqual(len(tags), 6)

            doc_header = tags.pop(0)
            self.assertEqual(doc_header.name, 'h2')
            self.assertEqual(doc_header.text, '1. doc')

            child_header = tags.pop(0)
            self.assertEqual(child_header.name, 'h3')
            self.assertEqual(child_header.text, '1.1. child')

            content = tags.pop(0)
            self.assertEqual(content.name, 'p')
            self.assertEqual(content.text, 'content')

            doc_header = tags.pop(0)
            self.assertEqual(doc_header.name, 'h2')
            self.assertEqual(doc_header.text, '2. section with spaces')

            doc_header = tags.pop(0)
            self.assertEqual(doc_header.name, 'h2')
            self.assertEqual(doc_header.text, '3. section_with_underscores')

            doc_header = tags.pop(0)
            self.assertEqual(doc_header.name, 'h2')
            self.assertEqual(doc_header.text, '4. section with a large name - Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent vitae volutpat ipsum, quis sodales eros. Aenean quis nunc quis leo aliquam gravida. Fusce accumsan nibh vitae enim ullamcorper iaculis. Duis eget augue dolor. Curabitur at enim elit. Nullam luctus mollis magna. Pellentesque pellentesque, leo quis suscipit finibus, diam justo convallis.')
