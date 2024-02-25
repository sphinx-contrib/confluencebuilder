# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestSdocSearch(ConfluenceTestCase):
    @setup_builder('confluence')
    def test_storage_sdoc_search_default_missing(self):
        """validate search is not added by default (storage)"""

        dataset = self.datasets / 'minimal'

        out_dir = self.build(dataset)

        fname_check = out_dir / 'search.conf'
        self.assertFalse(fname_check.is_file())

    @setup_builder('confluence')
    def test_storage_sdoc_search_explicit_disabled(self):
        """validate search generation can be disabled (storage)"""
        #
        # If a user adds a "search" document and does not want this extension to
        # automatically generate its contents, by disabling the search option
        # explicitly, the original search document should not be touched.

        dataset = self.datasets / 'sdoc' / 'search-placeholder'
        config = dict(self.config)
        config['confluence_include_search'] = False

        out_dir = self.build(dataset, config=config)

        with parse('search', out_dir) as data:
            placeholder = data.find('p')
            self.assertIsNotNone(placeholder)
            self.assertEqual(placeholder.text.strip(), 'placeholder')

    @setup_builder('confluence')
    def test_storage_sdoc_search_explicit_enabled(self):
        """validate search generation can be enabled (storage)"""
        #
        # Ensures the extension adds a "search" document; even if its not in a
        # documentation set's toctree.

        dataset = self.datasets / 'minimal'
        config = dict(self.config)
        config['confluence_include_search'] = True

        out_dir = self.build(dataset, config=config)

        with parse('search', out_dir) as data:
            search_macro = data.find('ac:structured-macro',
                {'ac:name': 'livesearch'})
            self.assertIsNotNone(search_macro)

    @setup_builder('confluence')
    def test_storage_sdoc_search_header_footer(self):
        """validate search generation includes header/footer (storage)"""
        #
        # Ensures that when the extension adds a "search" document; any custom
        # defined header/footer data is also injected into the document.

        dataset = self.datasets / 'minimal'
        footer_tpl = str(self.templates_dir / 'sample-footer.tpl')
        header_tpl = str(self.templates_dir / 'sample-header.tpl')

        config = dict(self.config)
        config['confluence_include_search'] = True
        config['confluence_footer_file'] = footer_tpl
        config['confluence_header_file'] = header_tpl

        out_dir = self.build(dataset, config=config)

        with parse('search', out_dir) as data:
            header_data = data.find().previousSibling.strip()
            self.assertEqual(header_data, 'header content')

            footer_data = data.find_all(recursive=False)[-1].nextSibling.strip()
            self.assertEqual(footer_data, 'footer content')

    @setup_builder('confluence')
    def test_storage_sdoc_search_implicit_enabled_toctree(self):
        """validate search generation is auto-added via toctree (storage)"""
        #
        # If a "search" document is found in the documentation set's toctree,
        # the document should be generated.

        dataset = self.datasets / 'sdoc' / 'search-placeholder'

        out_dir = self.build(dataset)

        with parse('search', out_dir) as data:
            search_macro = data.find('ac:structured-macro',
                {'ac:name': 'livesearch'})
            self.assertIsNotNone(search_macro)
