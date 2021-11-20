# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestSdocSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.container = os.path.join(test_dir, 'datasets')
        cls.template_dir = os.path.join(test_dir, 'templates')

    def test_storage_sdoc_search_default_missing(self):
        """validate search is not added by default (storage)"""

        dataset = os.path.join(self.container, 'minimal')

        out_dir = build_sphinx(dataset, config=self.config)

        fname_check = os.path.join(out_dir, 'search.conf')
        self.assertFalse(os.path.exists(fname_check))

    def test_storage_sdoc_search_explicit_disabled(self):
        """validate search generation can be disabled (storage)"""
        #
        # If a user adds a "search" document and does not want this extension to
        # automatically generate its contents, by disabling the search option
        # explicitly, the original search document should not be touched.

        dataset = os.path.join(self.container, 'sdoc', 'search-placeholder')
        config = dict(self.config)
        config['confluence_include_search'] = False

        out_dir = build_sphinx(dataset, config=config)

        with parse('search', out_dir) as data:
            placeholder = data.find('p')
            self.assertIsNotNone(placeholder)
            self.assertEqual(placeholder.text.strip(), 'placeholder')

    def test_storage_sdoc_search_explicit_enabled(self):
        """validate search generation can be enabled (storage)"""
        #
        # Ensures the extension adds a "search" document; even if its not in a
        # documentation set's toctree.

        dataset = os.path.join(self.container, 'minimal')
        config = dict(self.config)
        config['confluence_include_search'] = True

        out_dir = build_sphinx(dataset, config=config)

        with parse('search', out_dir) as data:
            search_macro = data.find('ac:structured-macro',
                {'ac:name': 'livesearch'})
            self.assertIsNotNone(search_macro)

    def test_storage_sdoc_search_header_footer(self):
        """validate search generation includes header/footer (storage)"""
        #
        # Ensures that when the extension adds a "search" document; any custom
        # defined header/footer data is also injected into the document.

        dataset = os.path.join(self.container, 'minimal')
        footer_tpl = os.path.join(self.template_dir, 'sample-footer.tpl')
        header_tpl = os.path.join(self.template_dir, 'sample-header.tpl')

        config = dict(self.config)
        config['confluence_include_search'] = True
        config['confluence_footer_file'] = footer_tpl
        config['confluence_header_file'] = header_tpl

        out_dir = build_sphinx(dataset, config=config)

        with parse('search', out_dir) as data:
            header_data = data.find().previousSibling.strip()
            self.assertEqual(header_data, 'header content')

            footer_data = data.find_all(recursive=False)[-1].nextSibling.strip()
            self.assertEqual(footer_data, 'footer content')

    def test_storage_sdoc_search_implicit_enabled_toctree(self):
        """validate search generation is auto-added via toctree (storage)"""
        #
        # If a "search" document is found in the documentation set's toctree,
        # the document should be generated.

        dataset = os.path.join(self.container, 'sdoc', 'search-placeholder')

        out_dir = build_sphinx(dataset, config=self.config)

        with parse('search', out_dir) as data:
            search_macro = data.find('ac:structured-macro',
                {'ac:name': 'livesearch'})
            self.assertIsNotNone(search_macro)
