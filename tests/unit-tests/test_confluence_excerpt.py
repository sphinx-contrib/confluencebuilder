# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceExcerpt(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'excerpt')

    @setup_builder('confluence')
    def test_storage_confluence_excerpt_directive_expected(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            excerpt_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'excerpt'})
            self.assertIsNotNone(excerpt_macros)
            self.assertEqual(len(excerpt_macros), 5)

            # excerpt macro without no options
            excerpt_macro = excerpt_macros.pop(0)

            name = excerpt_macro.find('ac:parameter', {'ac:name': 'name'})
            self.assertIsNone(name)

            rich_body = excerpt_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'no options')

            # excerpt macro with name
            excerpt_macro = excerpt_macros.pop(0)

            name = excerpt_macro.find('ac:parameter', {'ac:name': 'name'})
            self.assertIsNotNone(name)
            self.assertEqual(name.text, 'test')

            rich_body = excerpt_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'excerpt with name')

            # excerpt macro that is hidden
            excerpt_macro = excerpt_macros.pop(0)

            hidden = excerpt_macro.find('ac:parameter', {'ac:name': 'hidden'})
            self.assertIsNotNone(hidden)
            self.assertEqual(hidden.text, 'true')

            # excerpt macro with explicit BLOCK type
            excerpt_macro = excerpt_macros.pop(0)

            output_type = excerpt_macro.find('ac:parameter',
                {'ac:name': 'atlassian-macro-output-type'})
            self.assertIsNotNone(output_type)
            self.assertEqual(output_type.text, 'BLOCK')

            # excerpt macro with explicit INLINE type
            excerpt_macro = excerpt_macros.pop(0)

            output_type = excerpt_macro.find('ac:parameter',
                {'ac:name': 'atlassian-macro-output-type'})
            self.assertIsNotNone(output_type)
            self.assertEqual(output_type.text, 'INLINE')

        with parse('second', out_dir) as data:
            excerpt_include_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'excerpt-include'})
            self.assertIsNotNone(excerpt_include_macros)
            self.assertEqual(len(excerpt_include_macros), 5)

            # excerpt-include macro (simple)
            excerpt_include_macro = excerpt_include_macros.pop(0)

            doc_param = excerpt_include_macro.find('ac:parameter',
                {'ac:name': ''})
            self.assertIsNotNone(doc_param)

            doc_link = doc_param.find('ac:link')
            self.assertIsNotNone(doc_link)

            page_ref = doc_link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'], 'index')
            self.assertTrue('ri:space-key' not in page_ref)

            # excerpt-include macro with named excerpt
            excerpt_include_macro = excerpt_include_macros.pop(0)

            name = excerpt_include_macro.find('ac:parameter',
                {'ac:name': 'name'})
            self.assertIsNotNone(name)

            # excerpt-include macro with no panel
            excerpt_include_macro = excerpt_include_macros.pop(0)

            nopanel = excerpt_include_macro.find('ac:parameter',
                {'ac:name': 'nopanel'})
            self.assertIsNotNone(nopanel)
            self.assertEqual(nopanel.text, 'true')

            # excerpt-include macro (external page; inside space)
            excerpt_include_macro = excerpt_include_macros.pop(0)

            doc_param = excerpt_include_macro.find('ac:parameter',
                {'ac:name': ''})
            self.assertIsNotNone(doc_param)

            doc_link = doc_param.find('ac:link')
            self.assertIsNotNone(doc_link)

            page_ref = doc_link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'], 'My excerpt page')
            self.assertTrue('ri:space-key' not in page_ref)

            # excerpt-include macro (external page; outside space)
            excerpt_include_macro = excerpt_include_macros.pop(0)

            doc_param = excerpt_include_macro.find('ac:parameter',
                {'ac:name': ''})
            self.assertIsNotNone(doc_param)

            doc_link = doc_param.find('ac:link')
            self.assertIsNotNone(doc_link)

            page_ref = doc_link.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'], 'My excerpt page2')
            self.assertEqual(page_ref['ri:space-key'], 'TEST')
