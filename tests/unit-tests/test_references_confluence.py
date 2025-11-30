# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from importlib.util import find_spec
from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import unittest


class TestConfluenceReferencesConfluence(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        # skip myst_parser-related tests if the extension is not available
        if find_spec('myst_parser') is None:
            msg = 'myst_parser is not available'
            raise unittest.SkipTest(msg)

        super().setUpClass()

        cls.config['extensions'].append('myst_parser')
        cls.dataset = cls.datasets / 'references'

        # disable any anchor workarounds for testing
        cls.config['confluence_adv_disable_confcloud_74698'] = True

        # markdown headers
        cls.config['myst_enable_extensions'] = [
            'colon_fence',
        ]
        cls.config['myst_heading_anchors'] = 7

    @setup_builder('confluence')
    def test_storage_references_confluence(self):
        out_dir = self.build(self.dataset, relax=True)

        # expected page names
        rst_v1_first_name = 'reStructuredText v1 First'
        rst_v1_second_name = 'reStructuredText v1 Second'
        rst_v2_first_name = 'reStructuredText v2 First'
        rst_v2_second_name = 'reStructuredText v2 Second'
        md_v1_first_name = 'Markdown v1 First'
        md_v1_second_name = 'Markdown v1 Second'
        md_v2_first_name = 'Markdown v2 First'
        md_v2_second_name = 'Markdown v2 Second'

        # initial checks -- verifying toc renders sane links to other pages
        with parse('index', out_dir) as data:
            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 8)

            expected_pages = [
                rst_v1_first_name,
                rst_v1_second_name,
                rst_v2_first_name,
                rst_v2_second_name,
                md_v1_first_name,
                md_v1_second_name,
                md_v2_first_name,
                md_v2_second_name,
            ]

            for (ac_link, page_name) in zip(
                    ac_links, expected_pages, strict=True):
                link_page = ac_link.find('ri:page')
                self.assertTrue(link_page.has_attr('ri:content-title'))
                self.assertEqual(link_page['ri:content-title'], page_name)

                link_body = ac_link.find('ac:link-body')
                self.assertIsNotNone(link_body)
                self.assertEqual(link_body.text, page_name)

        # rst-v1-first]
        # should have eight links:
        # - local-toc pointing to two headers
        # - each header pointing back to local-toc
        # - one href-link to top of page
        # - three link macros to internal points
        with parse('rst-v1-first', out_dir) as data:
            # ##########################################################
            # extract all anchors
            #  - 2x, anchor points on local-tocs
            #  - 1x, anchor in content
            # ##########################################################
            local_toc_entries = data.find_all('li')
            self.assertEqual(len(local_toc_entries), 2)

            # anchor in local-toc
            ltoc_entry = local_toc_entries.pop(0)
            ltoc_anchors = ltoc_entry.find_all(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertGreaterEqual(len(ltoc_anchors), 1)
            anchor_01_ids = []
            for ltoc_anchor in ltoc_anchors:
                anchor_param = ltoc_anchor.find('ac:parameter')
                self.assertIsNotNone(anchor_param)
                anchor_01_ids.append(anchor_param.text)

            # anchor in local-toc
            ltoc_entry = local_toc_entries.pop(0)
            ltoc_anchors = ltoc_entry.find_all(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertGreaterEqual(len(ltoc_anchors), 1)
            anchor_02_ids = []
            for ltoc_anchor in ltoc_anchors:
                anchor_param = ltoc_anchor.find('ac:parameter')
                self.assertIsNotNone(anchor_param)
                anchor_02_ids.append(anchor_param.text)

            # anchor after pre-content
            content_element = data.find('p', text='pre-content')
            self.assertIsNotNone(content_element)
            anchor_container = content_element.next_sibling
            ltoc_anchor = anchor_container.find(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertIsNotNone(ltoc_anchor)
            anchor_param = ltoc_anchor.find('ac:parameter')
            self.assertIsNotNone(anchor_param)
            anchor_03_id = anchor_param.text

            # ##########################################################
            # find the expected ac:link macros
            # ##########################################################
            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 7)

            # local-toc link down to a header
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'AnExtraHeader')
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # local-toc link down to a header
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'AnExtraHeader.1')
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # header link to a local-toc entry
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertIn(ac_link['ac:anchor'], anchor_01_ids)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # header link to a local-toc entry
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertIn(ac_link['ac:anchor'], anchor_02_ids)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # body link to sub-header on this page
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'AnExtraHeader')
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # body link to mid-way in the content section
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], anchor_03_id)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'content')

            # body link to second sub-header on this page
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'AnExtraHeader.1')
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # ##########################################################
            # find the link a-href link to the top
            # ##########################################################
            top_link = data.find('a')
            self.assertIsNotNone(top_link)
            self.assertTrue(top_link.has_attr('href'))
            self.assertEqual(top_link['href'], '#top')
            self.assertEqual(top_link.text, rst_v1_first_name)

        # rst-v1-second]
        # should have eight links
        with parse('rst-v1-second', out_dir) as data:
            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 8)

            # link to the very top of the main page (v1)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'reStructuredTextv1First')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, rst_v1_first_name)

            # link to the sub-header on the main page (v1)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'AnExtraHeader')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # link mid-way in the content section on the main page (v1)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'main-rst-v1-subcontent')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'content 1')

            # link to the second sub-header on the main page (v1)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'AnExtraHeader.1')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # link to the very top of the main page (v2)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'reStructuredText-v2-First')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, rst_v2_first_name)

            # link to the sub-header on the main page (v2)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'An-Extra-Header')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # link mid-way in the content section on the main page (v2)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'main-rst-v2-subcontent')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'content 2')

            # link to the second sub-header on the main page (v2)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'An-Extra-Header.1')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

        # rst-v2-first]
        # should have eight links:
        # - local-toc pointing to two headers
        # - each header pointing back to local-toc
        # - one href-link to top of page
        # - three link macros to internal points
        with parse('rst-v2-first', out_dir) as data:
            # ##########################################################
            # extract all anchors
            #  - 2x, anchor points on local-tocs
            #  - 1x, anchor in content
            # ##########################################################
            local_toc_entries = data.find_all('li')
            self.assertEqual(len(local_toc_entries), 2)

            # anchor in local-toc
            ltoc_entry = local_toc_entries.pop(0)
            ltoc_anchors = ltoc_entry.find_all(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertGreaterEqual(len(ltoc_anchors), 1)
            anchor_01_ids = []
            for ltoc_anchor in ltoc_anchors:
                anchor_param = ltoc_anchor.find('ac:parameter')
                self.assertIsNotNone(anchor_param)
                anchor_01_ids.append(anchor_param.text)

            # anchor in local-toc
            ltoc_entry = local_toc_entries.pop(0)
            ltoc_anchors = ltoc_entry.find_all(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertGreaterEqual(len(ltoc_anchors), 1)
            anchor_02_ids = []
            for ltoc_anchor in ltoc_anchors:
                anchor_param = ltoc_anchor.find('ac:parameter')
                self.assertIsNotNone(anchor_param)
                anchor_02_ids.append(anchor_param.text)

            # anchor after pre-content
            content_element = data.find('p', text='pre-content')
            self.assertIsNotNone(content_element)
            anchor_container = content_element.next_sibling
            ltoc_anchor = anchor_container.find(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertIsNotNone(ltoc_anchor)
            anchor_param = ltoc_anchor.find('ac:parameter')
            self.assertIsNotNone(anchor_param)
            anchor_03_id = anchor_param.text

            # ##########################################################
            # find the expected ac:link macros
            # ##########################################################
            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 2)

            # header link to a local-toc entry
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertIn(ac_link['ac:anchor'], anchor_01_ids)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # header link to a local-toc entry
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertIn(ac_link['ac:anchor'], anchor_02_ids)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # ##########################################################
            # find the expected a-href links
            # ##########################################################
            a_hrefs = data.find_all('a')
            self.assertEqual(len(a_hrefs), 6)

            # local-toc link down to a header
            a_href = a_hrefs.pop(0)
            self.assertIsNotNone(a_href)
            self.assertTrue(a_href.has_attr('href'))
            self.assertEqual(a_href['href'], '#An-Extra-Header')
            self.assertEqual(a_href.text, 'An Extra Header')

            # local-toc link down to a header
            a_href = a_hrefs.pop(0)
            self.assertIsNotNone(a_href)
            self.assertTrue(a_href.has_attr('href'))
            self.assertEqual(a_href['href'], '#An-Extra-Header.1')
            self.assertEqual(a_href.text, 'An Extra Header')

            # body link to top on this page
            a_href = a_hrefs.pop(0)
            self.assertIsNotNone(a_href)
            self.assertTrue(a_href.has_attr('href'))
            self.assertEqual(a_href['href'], '#top')
            self.assertEqual(a_href.text, rst_v2_first_name)

            # body link to sub-header on this page
            a_href = a_hrefs.pop(0)
            self.assertIsNotNone(a_href)
            self.assertTrue(a_href.has_attr('href'))
            self.assertEqual(a_href['href'], '#An-Extra-Header')
            self.assertEqual(a_href.text, 'An Extra Header')

            # body link to mid-way in the content section
            a_href = a_hrefs.pop(0)
            self.assertIsNotNone(a_href)
            self.assertTrue(a_href.has_attr('href'))
            self.assertEqual(a_href['href'], f'#{anchor_03_id}')
            self.assertEqual(a_href.text, 'content')

            # body link to second sub-header on this page
            a_href = a_hrefs.pop(0)
            self.assertIsNotNone(a_href)
            self.assertTrue(a_href.has_attr('href'))
            self.assertEqual(a_href['href'], '#An-Extra-Header.1')
            self.assertEqual(a_href.text, 'An Extra Header')

        # rst-v2-second]
        # should have eight links
        with parse('rst-v2-second', out_dir) as data:
            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 8)

            # link to the very top of the main page (v1)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'reStructuredTextv1First')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, rst_v1_first_name)

            # link to the sub-header on the main page (v1)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'AnExtraHeader')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # link mid-way in the content section on the main page (v1)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'main-rst-v1-subcontent')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'content a')

            # link to the second sub-header on the main page (v1)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'AnExtraHeader.1')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # link to the very top of the main page (v2)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'reStructuredText-v2-First')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, rst_v2_first_name)

            # link to the sub-header on the main page (v2)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'An-Extra-Header')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

            # link mid-way in the content section on the main page (v2)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'main-rst-v2-subcontent')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'content b')

            # link to the second sub-header on the main page (v2)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'An-Extra-Header.1')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], rst_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'An Extra Header')

        # md-v1-second]
        with parse('md-v1-second', out_dir) as data:
            # ##########################################################
            # extract all anchors
            #  - 2x, anchors in headers
            # ##########################################################
            header_entries = data.find_all('h2')
            self.assertEqual(len(header_entries), 2)

            # anchor in first header
            header_entry = header_entries.pop(0)
            header_anchors = header_entry.find_all(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertGreaterEqual(len(ltoc_anchors), 1)
            anchor_01_ids = []
            for header_anchor in header_anchors:
                anchor_param = header_anchor.find('ac:parameter')
                self.assertIsNotNone(anchor_param)
                anchor_01_ids.append(anchor_param.text)

            # anchor in second header
            header_entry = header_entries.pop(0)
            header_anchors = header_entry.find_all(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertGreaterEqual(len(ltoc_anchors), 1)
            anchor_02_ids = []
            for header_anchor in header_anchors:
                anchor_param = header_anchor.find('ac:parameter')
                self.assertIsNotNone(anchor_param)
                anchor_02_ids.append(anchor_param.text)

            # ##########################################################
            # find the expected ac:link macros
            # ##########################################################
            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 7)

            # heading jump to other heading
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertIn(ac_link['ac:anchor'], anchor_01_ids)
            link_page = ac_link.find('ri:page')
            self.assertIsNone(link_page)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, '(jump above)')

            # link to the sub-heading on this page
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertIn(ac_link['ac:anchor'], anchor_01_ids)
            link_page = ac_link.find('ri:page')
            self.assertIsNone(link_page)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text,
                'Markdown v1 Second sub-heading')

            # link to the second sub-heading on this page
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertIn(ac_link['ac:anchor'], anchor_02_ids)
            link_page = ac_link.find('ri:page')
            self.assertIsNone(link_page)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text,
                'Markdown v1 Second sub-heading (jump above)')

            # link to the top of the second page (v1)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'Markdownv1First')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], md_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'link text 1')

            # link to the second page's (v1) sub-heading
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'Markdownv1Firstsub-heading')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], md_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'link text 2')

            # link to the top of the second page (v2)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'Markdown-v2-First')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], md_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'link text 3')

            # link to the second page's (v2) sub-heading
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'],
                'Markdown-v2-First-sub-heading')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], md_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'link text 4')

        # md-v2-second]
        with parse('md-v2-second', out_dir) as data:
            # ##########################################################
            # extract all anchors
            #  - 2x, anchors in headers
            # ##########################################################
            header_entries = data.find_all('h2')
            self.assertEqual(len(header_entries), 2)

            # anchor in first header
            header_entry = header_entries.pop(0)
            header_anchors = header_entry.find_all(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertGreaterEqual(len(ltoc_anchors), 1)
            anchor_01_ids = []
            for header_anchor in header_anchors:
                anchor_param = header_anchor.find('ac:parameter')
                self.assertIsNotNone(anchor_param)
                anchor_01_ids.append(anchor_param.text)

            # anchor in second header
            header_entry = header_entries.pop(0)
            header_anchors = header_entry.find_all(
                'ac:structured-macro', {'ac:name': 'anchor'})
            self.assertGreaterEqual(len(ltoc_anchors), 1)
            anchor_02_ids = []
            for header_anchor in header_anchors:
                anchor_param = header_anchor.find('ac:parameter')
                self.assertIsNotNone(anchor_param)
                anchor_02_ids.append(anchor_param.text)

            # ##########################################################
            # find the expected ac:link macros
            # ##########################################################
            ac_links = data.find_all('ac:link')
            self.assertEqual(len(ac_links), 4)

            # link to the top of the second page (v1)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'Markdown-v2-First')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], md_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'link text a')

            # link to the second page's (v1) sub-heading
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'],
                'Markdown-v2-First-sub-heading')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], md_v2_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'link text b')

            # link to the top of the second page (v2)
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'Markdownv1First')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], md_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'link text c')

            # link to the second page's (v2) sub-heading
            ac_link = ac_links.pop(0)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'Markdownv1Firstsub-heading')
            link_page = ac_link.find('ri:page')
            self.assertTrue(link_page.has_attr('ri:content-title'))
            self.assertEqual(link_page['ri:content-title'], md_v1_first_name)
            ac_link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(ac_link_body)
            self.assertEqual(ac_link_body.text, 'link text d')

            # ##########################################################
            # find the expected a-href links
            # ##########################################################
            a_hrefs = data.find_all('a')
            self.assertEqual(len(a_hrefs), 4)

            # heading jump to other heading
            a_href = a_hrefs.pop(0)
            self.assertIsNotNone(a_href)
            self.assertTrue(a_href.has_attr('href'))
            self.assertEqual(a_href['href'], '#Markdown-v2-Second-sub-heading')
            self.assertEqual(a_href.text, '(jump above)')

            # link to the top of this page
            a_href = a_hrefs.pop(0)
            self.assertIsNotNone(a_href)
            self.assertTrue(a_href.has_attr('href'))
            self.assertEqual(a_href['href'], '#top')
            self.assertEqual(a_href.text, md_v2_second_name)

            # link to the sub-heading on this page
            a_href = a_hrefs.pop(0)
            self.assertIsNotNone(a_href)
            self.assertTrue(a_href.has_attr('href'))
            self.assertEqual(a_href['href'], '#Markdown-v2-Second-sub-heading')
            self.assertEqual(a_href.text, 'Markdown v2 Second sub-heading')

            # link to the second sub-heading on this page
            a_href = a_hrefs.pop(0)
            self.assertIsNotNone(a_href)
            self.assertTrue(a_href.has_attr('href'))
            self.assertEqual(a_href['href'],
                '#markdown-v2-second-sub-heading-jump-above')
            self.assertEqual(a_href.text,
                'Markdown v2 Second sub-heading (jump above)')
