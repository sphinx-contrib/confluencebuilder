# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceRstReferences(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.config['root_doc'] = 'references'
        cls.dataset = os.path.join(cls.datasets, 'rst', 'references')

    @setup_builder('confluence')
    def test_storage_rst_references(self):
        out_dir = self.build(self.dataset)

        with parse('references', out_dir) as data:
            a_tags = data.find_all('a')
            self.assertEqual(len(a_tags), 6)

            # basic links ##############################################

            # (link 1)
            a_tag = a_tags.pop(0)
            self.assertTrue(a_tag.has_attr('href'))
            self.assertEqual(a_tag['href'], 'https://www.example.com/')
            self.assertEqual(a_tag.text, 'https://www.example.com/')

            # (link 2)
            a_tag = a_tags.pop(0)
            self.assertTrue(a_tag.has_attr('href'))
            self.assertEqual(a_tag['href'], 'mailto:someone@example.com')
            self.assertEqual(a_tag.text, 'someone@example.com')

            # (link 3)
            a_tag = a_tags.pop(0)
            self.assertTrue(a_tag.has_attr('href'))
            self.assertEqual(a_tag['href'], 'https://example.com/')
            self.assertEqual(a_tag.text, 'custom name')

            # (link 4)
            a_tag = a_tags.pop(0)
            self.assertTrue(a_tag.has_attr('href'))
            self.assertEqual(a_tag['href'], 'https://example.com/')
            self.assertEqual(a_tag.text, 'a link')

            # (link 5)
            a_tag = a_tags.pop(0)
            self.assertTrue(a_tag.has_attr('href'))
            self.assertEqual(a_tag['href'], 'https://example.org/')
            self.assertEqual(a_tag.renderContents().decode(), '&gt;')

            # (link 6)
            a_tag = a_tags.pop(0)
            self.assertTrue(a_tag.has_attr('href'))
            self.assertEqual(a_tag['href'], 'https://example.com/')

            stronged = a_tag.find('strong')
            self.assertIsNotNone(stronged)
            self.assertEqual(stronged.text, 'a bolded link')

            # anchors ##################################################

            anchors = data.find_all('ac:structured-macro',
                {'ac:name': 'anchor'})
            self.assertEqual(len(anchors), 1)

            # (anchor 1)
            anchor = anchors.pop(0)

            anchor_id = anchor.find('ac:parameter')
            self.assertIsNotNone(anchor_id)
            self.assertEqual(anchor_id.text, 'my-reference-label1')

            # document links ###########################################

            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 4)

            # (ac-link 1) external document
            ac_link = ac_links.pop(0)

            page_ref = ac_link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'references-ref')

            link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'references-ref')

            # (ac-link 2) external document with custom label
            ac_link = ac_links.pop(0)

            page_ref = ac_link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'references-ref')

            link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'custom name')

            # (ac-link 3) link directly to section target
            ac_link = ac_links.pop(0)

            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'sub-section')

            link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'sub-section')

            # (ac-link 4) link to anchor
            ac_link = ac_links.pop(0)

            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'my-reference-label1')

            link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'internal anchor')

        with parse('references-ref', out_dir) as data:
            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 4)

            # (ac-link 1) external document
            ac_link = ac_links.pop(0)

            page_ref = ac_link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'references')

            link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'references')

            # (ac-link 2) external document with custom label
            ac_link = ac_links.pop(0)

            page_ref = ac_link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'references')

            link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'custom name')

            # (ac-link 3) link directly to section target
            ac_link = ac_links.pop(0)

            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'my-reference-label1')

            page_ref = ac_link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'references')

            link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'references anchor')

            # (ac-link 4) link to anchor
            ac_link = ac_links.pop(0)

            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'sub-section')

            page_ref = ac_link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'references')

            link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'references section')
