# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestSdocGenindex(ConfluenceTestCase):
    @setup_builder('confluence')
    def test_storage_sdoc_genindex_default_missing_confluence(self):
        """validate genindex is not added by default (confluence)"""

        dataset = os.path.join(self.datasets, 'minimal')

        out_dir = self.build(dataset)

        fname_check = os.path.join(out_dir, 'genindex.conf')
        self.assertFalse(os.path.exists(fname_check))

    @setup_builder('singleconfluence')
    def test_storage_sdoc_genindex_default_missing_singleconfluence(self):
        """validate genindex is not added by default (singleconfluence)"""

        dataset = os.path.join(self.datasets, 'minimal')

        out_dir = self.build(dataset)

        fname_check = os.path.join(out_dir, 'genindex.conf')
        self.assertFalse(os.path.exists(fname_check))

    @setup_builder('confluence')
    def test_storage_sdoc_genindex_explicit_disabled(self):
        """validate genindex generation can be disabled (storage)"""
        #
        # If a user adds a "genindex" document and does not want this extension
        # to automatically generate its contents, by disabling the genindex
        # option explicitly, the original genindex document should not be
        # touched.

        dataset = os.path.join(self.datasets, 'sdoc', 'genindex-placeholder')
        config = dict(self.config)
        config['confluence_use_index'] = False

        out_dir = self.build(dataset, config=config)

        with parse('genindex', out_dir) as data:
            placeholder = data.find('p')
            self.assertIsNotNone(placeholder)
            self.assertEqual(placeholder.text.strip(), 'placeholder')

    @setup_builder('confluence')
    def test_storage_sdoc_genindex_explicit_enabled(self):
        """validate genindex generation can be enabled (storage)"""
        #
        # Ensures the extension adds a "genindex" document; even if its not in a
        # documentation set's toctree.

        dataset = os.path.join(self.datasets, 'sdoc', 'genindex')
        config = dict(self.config)
        config['confluence_use_index'] = True

        out_dir = self.build(dataset, config=config)

        with parse('genindex', out_dir) as data:
            link_tags = data.find_all('ac:link')
            self.assertIsNotNone(link_tags)

            section_link = link_tags.pop(0)
            self.assertIsNotNone(section_link)

            index_link = link_tags.pop(0)
            self.assertIsNotNone(index_link)
            self.assertTrue(index_link.has_attr('ac:anchor'))

            link_body = index_link.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'test')

    @setup_builder('confluence')
    def test_storage_sdoc_genindex_header_footer(self):
        """validate genindex generation includes header/footer (storage)"""
        #
        # Ensures that when the extension adds a "genindex" document; any custom
        # defined header/footer data is also injected into the document.

        dataset = os.path.join(self.datasets, 'sdoc', 'genindex')
        footer_tpl = os.path.join(self.templates_dir, 'sample-footer.tpl')
        header_tpl = os.path.join(self.templates_dir, 'sample-header.tpl')

        config = dict(self.config)
        config['confluence_use_index'] = True
        config['confluence_footer_file'] = footer_tpl
        config['confluence_header_file'] = header_tpl

        out_dir = self.build(dataset, config=config)

        with parse('genindex', out_dir) as data:
            header_data = data.find().previousSibling.strip()
            self.assertEqual(header_data, 'header content')

            footer_data = data.find_all(recursive=False)[-1].nextSibling.strip()
            self.assertEqual(footer_data, 'footer content')

    @setup_builder('confluence')
    def test_storage_sdoc_genindex_implicit_enabled_toctree(self):
        """validate genindex generation is auto-added via toctree (storage)"""
        #
        # If a "genindex" document is found in the documentation set's toctree,
        # the document should be generated.

        dataset = os.path.join(self.datasets, 'sdoc', 'genindex-placeholder')

        out_dir = self.build(dataset)

        with parse('genindex', out_dir) as data:
            link_tags = data.find_all('ac:link')
            self.assertIsNotNone(link_tags)

            section_link = link_tags.pop(0)
            self.assertIsNotNone(section_link)

            index_link = link_tags.pop(0)
            self.assertIsNotNone(index_link)
            self.assertTrue(index_link.has_attr('ac:anchor'))

            link_body = index_link.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'test')
