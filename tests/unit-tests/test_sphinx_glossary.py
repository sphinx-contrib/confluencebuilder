# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2020-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceSphinxDomains(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceSphinxDomains, cls).setUpClass()

        cls.config['root_doc'] = 'glossary'
        cls.dataset = os.path.join(cls.datasets, 'glossary')

    @setup_builder('confluence')
    def test_storage_sphinx_glossary_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('glossary', out_dir) as data:
            # glossary list
            definitions = data.find('dl')
            self.assertIsNotNone(definitions)

            glossary1 = definitions.find('dt', text='glossary 1')
            self.assertIsNotNone(glossary1)

            glossary1_data = glossary1.find_next_sibling('dd')
            self.assertIsNotNone(glossary1_data)
            self.assertEqual(glossary1_data.name, 'dd')
            self.assertEqual(glossary1_data.text.strip(), 'content')

            glossary2 = definitions.find('dt', text='glossary 2')
            self.assertIsNotNone(glossary2)

            glossary3 = glossary2.find_next_sibling('dt')
            self.assertIsNotNone(glossary3)
            self.assertEqual(glossary3.name, 'dt')
            self.assertEqual(glossary3.text.strip(), 'glossary 3')

            glossary23_data = glossary3.find_next_sibling('dd')
            self.assertIsNotNone(glossary23_data)

            glossary23_contents = glossary23_data.find('p', recursive=False)
            self.assertIsNotNone(glossary23_contents)
            self.assertEqual(glossary23_contents.text.strip(), 'content')

            glossary23_list = glossary23_data.find('ul', recursive=False)
            self.assertIsNotNone(glossary23_list)

            # internal links to glossary entries
            link_tags = data.find_all('ac:link')
            self.assertIsNotNone(link_tags)
            self.assertEqual(len(link_tags), 3)

            # (link 1)
            link_tag = link_tags.pop(0)
            self.assertTrue(link_tag.has_attr('ac:anchor'))
            self.assertEqual(link_tag['ac:anchor'], 'term-glossary-1')

            link_body = link_tag.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'glossary 1')

            # (link 2)
            link_tag = link_tags.pop(0)
            self.assertTrue(link_tag.has_attr('ac:anchor'))
            self.assertEqual(link_tag['ac:anchor'], 'term-glossary-2')

            link_body = link_tag.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'glossary 2')

            # (link 3)
            link_tag = link_tags.pop(0)
            self.assertTrue(link_tag.has_attr('ac:anchor'))
            self.assertEqual(link_tag['ac:anchor'], 'term-glossary-3')

            link_body = link_tag.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'glossary 3')

        with parse('glossary-ref', out_dir) as data:
            # external links to glossary entries
            link_tags = data.find_all('ac:link')
            self.assertIsNotNone(link_tags)
            self.assertEqual(len(link_tags), 3)

            # (link 1)
            link_tag = link_tags.pop(0)
            self.assertTrue(link_tag.has_attr('ac:anchor'))
            self.assertEqual(link_tag['ac:anchor'], 'term-glossary-1')

            page_ref = link_tag.find('ri:page', recursive=False)
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'glossary')

            link_body = link_tag.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'glossary 1')

            # (link 2)
            link_tag = link_tags.pop(0)
            self.assertTrue(link_tag.has_attr('ac:anchor'))
            self.assertEqual(link_tag['ac:anchor'], 'term-glossary-2')

            page_ref = link_tag.find('ri:page', recursive=False)
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'glossary')

            link_body = link_tag.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'glossary 2')

            # (link 3)
            link_tag = link_tags.pop(0)
            self.assertTrue(link_tag.has_attr('ac:anchor'))
            self.assertEqual(link_tag['ac:anchor'], 'term-glossary-3')

            page_ref = link_tag.find('ri:page', recursive=False)
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'glossary')

            link_body = link_tag.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'glossary 3')
