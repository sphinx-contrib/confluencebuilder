# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceRstCitations(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'citations'

    @setup_builder('confluence')
    def test_storage_rst_citations(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            # ##########################################################
            # citations
            # ##########################################################

            citation_link_containers = data.find_all('sup')
            self.assertEqual(len(citation_link_containers), 2)

            # citation a
            container = citation_link_containers.pop(0)
            ac_link = container.find('ac:link')
            self.assertIsNotNone(ac_link)

            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'cit01')

            link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, '[CIT01]')

            # leader anchor back to this citation a
            anchor_tag = container.find_previous_sibling()
            self.assertIsNotNone(anchor_tag)
            self.assertEqual(anchor_tag.name, 'ac:structured-macro')
            self.assertTrue(anchor_tag.has_attr('ac:name'))
            self.assertEqual(anchor_tag['ac:name'], 'anchor')

            anchor_param = anchor_tag.find('ac:parameter', recursive=False)
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'id1')

            # citation b
            container = citation_link_containers.pop(0)
            ac_link = container.find('ac:link')
            self.assertIsNotNone(ac_link)

            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'cit02')

            link_body = ac_link.find('ac:link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, '[CIT02]')

            # leader anchor back to this citation b
            anchor_tag = container.find_previous_sibling()
            self.assertIsNotNone(anchor_tag)
            self.assertEqual(anchor_tag.name, 'ac:structured-macro')
            self.assertTrue(anchor_tag.has_attr('ac:name'))
            self.assertEqual(anchor_tag['ac:name'], 'anchor')

            anchor_param = anchor_tag.find('ac:parameter', recursive=False)
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'id2')

            # ##########################################################
            # citation table
            # ##########################################################

            citation_table = data.find('table')
            self.assertIsNotNone(citation_table)

            citation_rows = citation_table.find_all('tr')
            self.assertEqual(len(citation_rows), 2)

            # citation a
            tds = citation_rows[0].find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            anchor_tag = tds[0].find('ac:structured-macro',
                {'ac:name': 'anchor'})
            self.assertIsNotNone(anchor_tag)
            anchor_param = anchor_tag.find('ac:parameter')
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'cit01')

            ac_link = tds[0].find('ac:link')
            self.assertIsNotNone(ac_link)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'id1')
            link_body = ac_link.find('ac:plain-text-link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, '[CIT01]')

            self.assertEqual(tds[1].text.strip(), 'citation 1')

            # citation b
            tds = citation_rows[1].find_all('td', recursive=False)
            self.assertEqual(len(tds), 2)

            anchor_tag = tds[0].find('ac:structured-macro',
                {'ac:name': 'anchor'})
            self.assertIsNotNone(anchor_tag)
            anchor_param = anchor_tag.find('ac:parameter')
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'cit02')

            ac_link = tds[0].find('ac:link')
            self.assertIsNotNone(ac_link)
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], 'id2')
            link_body = ac_link.find('ac:plain-text-link-body')
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, '[CIT02]')

            self.assertEqual(tds[1].text.strip(), 'citation 2')
