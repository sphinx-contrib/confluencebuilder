# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceSphinxToctree(ConfluenceTestCase):
    @setup_builder('confluence')
    def test_storage_sphinx_toctree_caption(self):
        dataset = self.datasets / 'toctree-caption'
        out_dir = self.build(dataset)

        with parse('index', out_dir) as data:
            root_toc = data.find('ul', recursive=False)
            self.assertIsNotNone(root_toc)

            caption = root_toc.findPrevious()
            self.assertIsNotNone(caption)
            self.assertEqual(caption.text, 'toctree caption')

    @setup_builder('confluence')
    def test_storage_sphinx_toctree_default(self):
        dataset = self.datasets / 'toctree-default'

        out_dir = self.build(dataset)

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

    @setup_builder('confluence')
    def test_storage_sphinx_toctree_hidden(self):
        dataset = self.datasets / 'toctree-hidden'

        out_dir = self.build(dataset)

        with parse('index', out_dir) as data:
            # expect no content with a hidden toctree
            self.assertEqual(data.text, '')

    @setup_builder('confluence')
    def test_storage_sphinx_toctree_maxdepth(self):
        dataset = self.datasets / 'toctree-maxdepth'

        out_dir = self.build(dataset)

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

    @setup_builder('confluence')
    def test_storage_sphinx_toctree_numbered_default(self):
        dataset = self.datasets / 'toctree-numbered'

        out_dir = self.build(dataset)

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

    @setup_builder('confluence')
    def test_storage_sphinx_toctree_numbered_depth(self):
        dataset = self.datasets / 'toctree-numbered-depth'

        out_dir = self.build(dataset)

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

    @setup_builder('confluence')
    def test_storage_sphinx_toctree_numbered_disable(self):
        dataset = self.datasets / 'toctree-numbered'

        config = dict(self.config)
        config['confluence_add_secnumbers'] = False

        out_dir = self.build(dataset, config=config)

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

    @setup_builder('confluence')
    def test_storage_sphinx_toctree_numbered_secnumbers_suffix_empty(self):
        """validate toctree secnumber supports empty str (storage)"""
        #
        # Ensure that the toctree secnumber suffix value can be set to an
        # empty string.

        dataset = self.datasets / 'toctree-numbered'

        config = dict(self.config)
        config['confluence_secnumber_suffix'] = ''

        out_dir = self.build(dataset, config=config)

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

    @setup_builder('confluence')
    def test_storage_sphinx_toctree_numbered_secnumbers_suffix_set(self):
        dataset = self.datasets / 'toctree-numbered'

        config = dict(self.config)
        config['confluence_secnumber_suffix'] = '!Z /+4'

        out_dir = self.build(dataset, config=config)

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
