# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceSphinxToctree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        cls.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_storage_sphinx_toctree_caption(self):
        dataset = os.path.join(self.test_dir, 'datasets', 'toctree-caption')
        out_dir = build_sphinx(dataset, config=self.config)

        with parse('index', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            caption = root_toc.findPrevious()
            self.assertIsNotNone(caption)
            self.assertEqual(caption.text, 'toctree caption')

    def test_storage_sphinx_toctree_child_macro(self):
        dataset = os.path.join(self.test_dir, 'datasets', 'toctree-default')

        config = dict(self.config)
        config['confluence_adv_hierarchy_child_macro'] = True
        config['confluence_page_hierarchy'] = True

        # relax due to this test (confluence_adv_hierarchy_child_macro) being
        # deprecated
        out_dir = build_sphinx(dataset, config=config, relax=True)

        with parse('index', out_dir) as data:
            macro = data.find('ac:structured-macro', recursive=False)
            self.assertIsNotNone(macro)
            self.assertTrue(macro.has_attr('ac:name'))
            self.assertEqual(macro['ac:name'], 'children')

            all_param = macro.find('ac:parameter', recursive=False)
            self.assertIsNotNone(all_param)
            self.assertTrue(all_param.has_attr('ac:name'))
            self.assertEqual(all_param['ac:name'], 'all')
            self.assertEqual(all_param.text, 'true')

    def test_storage_sphinx_toctree_default(self):
        dataset = os.path.join(self.test_dir, 'datasets', 'toctree-default')

        out_dir = build_sphinx(dataset, config=self.config)

        with parse('index', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            primary_docs = root_toc.findChildren('li', recursive=False)
            self.assertEqual(len(primary_docs), 2)

            # document-a group
            group = primary_docs[0]
            self._verify_link(group, 'doc-a')

            group_docs = group.find('ul', recursive=False)
            self.assertIsNotNone(group_docs)

            sub_docs = group_docs.findChildren('li', recursive=False)
            self.assertIsNotNone(sub_docs)
            self.assertEqual(len(sub_docs), 2)
            self._verify_link(sub_docs[0], 'doc-a1')
            self._verify_link(sub_docs[1], 'doc-a2')

            # document-b group
            group = primary_docs[1]
            self._verify_link(group, 'doc-b')

            subheader_group = group.find('ul', recursive=False)
            self.assertIsNotNone(subheader_group)

            subheader = subheader_group.find('li', recursive=False)
            self.assertIsNotNone(subheader)
            self._verify_link(subheader, 'doc-b', label='subheader',
                anchor='subheader')

            final_group = subheader.find('ul', recursive=False)
            self.assertIsNotNone(final_group)

            sub_docs = final_group.findChildren('li', recursive=False)
            self.assertIsNotNone(sub_docs)
            self.assertEqual(len(sub_docs), 1)
            self._verify_link(sub_docs[0], 'doc-b1')

    def test_storage_sphinx_toctree_hidden(self):
        dataset = os.path.join(self.test_dir, 'datasets', 'toctree-hidden')

        out_dir = build_sphinx(dataset, config=self.config)

        with parse('index', out_dir) as data:
            # expect no content with a hidden toctree
            self.assertEqual(data.text, '')

    def test_storage_sphinx_toctree_maxdepth(self):
        dataset = os.path.join(self.test_dir, 'datasets', 'toctree-maxdepth')

        out_dir = build_sphinx(dataset, config=self.config)

        with parse('index', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 1)

            doc = docs[0]
            doc_tags = doc.findChildren(recursive=False)
            self.assertIsNotNone(doc_tags)
            self.assertEqual(len(doc_tags), 1)  # no other links beyond depth
            self._verify_link(doc, 'doc')

    def test_storage_sphinx_toctree_numbered_default(self):
        dataset = os.path.join(self.test_dir, 'datasets', 'toctree-numbered')

        out_dir = build_sphinx(dataset, config=self.config)

        with parse('index', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 4)

            group = docs.pop(0)
            self._verify_link(group, '1. doc')

            group_docs = group.find('ul', recursive=False)
            self.assertIsNotNone(group_docs)

            sub_docs = group_docs.findChildren('li', recursive=False)
            self.assertIsNotNone(sub_docs)
            self.assertEqual(len(sub_docs), 1)
            self._verify_link(sub_docs[0], '1.1. child')

            group = docs.pop(0)
            self._verify_link(group, '1. doc',
                label='2. section with spaces')

            group = docs.pop(0)
            self._verify_link(group, '1. doc',
                label='3. section_with_underscores')

            group = docs.pop(0)
            self._verify_link(group, '1. doc',
                label='4. section with a large name - Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent vitae volutpat ipsum, quis sodales eros. Aenean quis nunc quis leo aliquam gravida. Fusce accumsan nibh vitae enim ullamcorper iaculis. Duis eget augue dolor. Curabitur at enim elit. Nullam luctus mollis magna. Pellentesque pellentesque, leo quis suscipit finibus, diam justo convallis.')

        with parse('doc', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 1)

            doc = docs[0]
            self._verify_link(doc, '1.1. child')

    def test_storage_sphinx_toctree_numbered_depth(self):
        dataset = os.path.join(self.test_dir, 'datasets', 'toctree-numbered-depth')

        out_dir = build_sphinx(dataset, config=self.config)

        with parse('index', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 1)

            group = docs[0]
            self._verify_link(group, '1. doc')

            group_docs = group.find('ul', recursive=False)
            self.assertIsNotNone(group_docs)

            sub_docs = group_docs.findChildren('li', recursive=False)
            self.assertIsNotNone(sub_docs)
            self.assertEqual(len(sub_docs), 1)
            self._verify_link(sub_docs[0], 'child')

        with parse('doc', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 1)

            doc = docs[0]
            self._verify_link(doc, 'child')

    def test_storage_sphinx_toctree_numbered_disable(self):
        dataset = os.path.join(self.test_dir, 'datasets', 'toctree-numbered')

        config = dict(self.config)
        config['confluence_add_secnumbers'] = False

        out_dir = build_sphinx(dataset, config=config)

        with parse('index', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 4)

            group = docs.pop(0)
            self._verify_link(group, 'doc')

            group_docs = group.find('ul', recursive=False)
            self.assertIsNotNone(group_docs)

            sub_docs = group_docs.findChildren('li', recursive=False)
            self.assertIsNotNone(sub_docs)
            self.assertEqual(len(sub_docs), 1)
            self._verify_link(sub_docs[0], 'child')

            group = docs.pop(0)
            self._verify_link(group, 'doc', label='section with spaces')

            group = docs.pop(0)
            self._verify_link(group, 'doc', label='section_with_underscores')

            group = docs.pop(0)
            self._verify_link(group, 'doc', label='section with a large name - Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent vitae volutpat ipsum, quis sodales eros. Aenean quis nunc quis leo aliquam gravida. Fusce accumsan nibh vitae enim ullamcorper iaculis. Duis eget augue dolor. Curabitur at enim elit. Nullam luctus mollis magna. Pellentesque pellentesque, leo quis suscipit finibus, diam justo convallis.')

        with parse('doc', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 1)

            doc = docs[0]
            self._verify_link(doc, 'child')

    def test_storage_sphinx_toctree_numbered_secnumbers_suffix_empty(self):
        """validate toctree secnumber supports empty str (storage)"""
        #
        # Ensure that the toctree secnumber suffix value can be set to an
        # empty string.

        dataset = os.path.join(self.test_dir, 'datasets', 'toctree-numbered')

        config = dict(self.config)
        config['confluence_secnumber_suffix'] = ''

        out_dir = build_sphinx(dataset, config=config)

        with parse('index', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 4)

            group = docs.pop(0)
            self._verify_link(group, '1doc')

            group_docs = group.find('ul', recursive=False)
            self.assertIsNotNone(group_docs)

            sub_docs = group_docs.findChildren('li', recursive=False)
            self.assertIsNotNone(sub_docs)
            self.assertEqual(len(sub_docs), 1)
            self._verify_link(sub_docs[0], '1.1child')

            group = docs.pop(0)
            self._verify_link(group, '1doc',
                label='2section with spaces')

            group = docs.pop(0)
            self._verify_link(group, '1doc',
                label='3section_with_underscores')

            group = docs.pop(0)
            self._verify_link(group, '1doc',
                label='4section with a large name - Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent vitae volutpat ipsum, quis sodales eros. Aenean quis nunc quis leo aliquam gravida. Fusce accumsan nibh vitae enim ullamcorper iaculis. Duis eget augue dolor. Curabitur at enim elit. Nullam luctus mollis magna. Pellentesque pellentesque, leo quis suscipit finibus, diam justo convallis.')

        with parse('doc', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 1)

            doc = docs[0]
            self._verify_link(doc, '1.1child')

    def test_storage_sphinx_toctree_numbered_secnumbers_suffix_set(self):
        dataset = os.path.join(self.test_dir, 'datasets', 'toctree-numbered')

        config = dict(self.config)
        config['confluence_secnumber_suffix'] = '!Z /+4'

        out_dir = build_sphinx(dataset, config=config)

        with parse('index', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 4)

            group = docs.pop(0)
            self._verify_link(group, '1!Z /+4doc')

            group_docs = group.find('ul', recursive=False)
            self.assertIsNotNone(group_docs)

            sub_docs = group_docs.findChildren('li', recursive=False)
            self.assertIsNotNone(sub_docs)
            self.assertEqual(len(sub_docs), 1)
            self._verify_link(sub_docs[0], '1.1!Z /+4child')

            group = docs.pop(0)
            self._verify_link(group, '1!Z /+4doc',
                label='2!Z /+4section with spaces')

            group = docs.pop(0)
            self._verify_link(group, '1!Z /+4doc',
                label='3!Z /+4section_with_underscores')

            group = docs.pop(0)
            self._verify_link(group, '1!Z /+4doc',
                label='4!Z /+4section with a large name - Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent vitae volutpat ipsum, quis sodales eros. Aenean quis nunc quis leo aliquam gravida. Fusce accumsan nibh vitae enim ullamcorper iaculis. Duis eget augue dolor. Curabitur at enim elit. Nullam luctus mollis magna. Pellentesque pellentesque, leo quis suscipit finibus, diam justo convallis.')

        with parse('doc', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            docs = root_toc.findChildren('li', recursive=False)
            self.assertIsNotNone(docs)
            self.assertEqual(len(docs), 1)

            doc = docs[0]
            self._verify_link(doc, '1.1!Z /+4child')

    def _verify_link(self, entity, title, label=None, anchor=None):
        label = label if label else title

        ac_link = entity.find('ac:link', recursive=False)
        self.assertIsNotNone(ac_link)
        if anchor:
            self.assertTrue(ac_link.has_attr('ac:anchor'))
            self.assertEqual(ac_link['ac:anchor'], anchor)

        page_ref = ac_link.find('ri:page', recursive=False)
        self.assertIsNotNone(page_ref)
        self.assertTrue(page_ref.has_attr('ri:content-title'))
        self.assertEqual(page_ref['ri:content-title'], title)

        link_body = ac_link.find('ac:link-body', recursive=False)
        self.assertIsNotNone(link_body)
        self.assertEqual(link_body.text, label)
