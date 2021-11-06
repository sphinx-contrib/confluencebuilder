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


class TestSdocModindex(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.container = os.path.join(test_dir, 'datasets')
        self.template_dir = os.path.join(test_dir, 'templates')

    def test_storage_sdoc_modindex_default_missing(self):
        """validate modindex is not added by default (storage)"""

        dataset = os.path.join(self.container, 'minimal')

        out_dir = build_sphinx(dataset, config=self.config)

        fname_check = os.path.join(out_dir, 'py-modindex.conf')
        self.assertFalse(os.path.exists(fname_check))

    def test_storage_sdoc_modindex_enabled(self):
        """validate modindex generation can be enabled (storage)"""
        #
        # Ensures the extension adds a "py-modindex" document when the domain
        # indices option is assigned to include the domain type.

        dataset = os.path.join(self.container, 'sdoc', 'py-modindex')
        config = dict(self.config)
        config['confluence_domain_indices'] = [
            'py-modindex',
        ]

        out_dir = build_sphinx(dataset, config=config)

        with parse('py-modindex', out_dir) as data:
            link_tags = data.find_all('ac:link')
            self.assertIsNotNone(link_tags)

            section_link = link_tags.pop(0)
            self.assertIsNotNone(section_link)

            index_link = link_tags.pop(0)
            self.assertIsNotNone(index_link)
            self.assertTrue(index_link.has_attr('ac:anchor'))

            link_body = index_link.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'Timer')

    def test_storage_sdoc_modindex_enabled_bool(self):
        """validate modindex generation can be bool-enabled (storage)"""
        #
        # Ensures the extension adds a "py-modindex" document when the domain
        # indices option is assigned to a `True` value.

        dataset = os.path.join(self.container, 'sdoc', 'py-modindex')
        config = dict(self.config)
        config['confluence_domain_indices'] = True

        out_dir = build_sphinx(dataset, config=config)

        with parse('py-modindex', out_dir) as data:
            link_tags = data.find_all('ac:link')
            self.assertIsNotNone(link_tags)

            section_link = link_tags.pop(0)
            self.assertIsNotNone(section_link)

            index_link = link_tags.pop(0)
            self.assertIsNotNone(index_link)
            self.assertTrue(index_link.has_attr('ac:anchor'))

            link_body = index_link.find('ac:link-body', recursive=False)
            self.assertIsNotNone(link_body)
            self.assertEqual(link_body.text, 'Timer')

    def test_storage_sdoc_modindex_header_footer(self):
        """validate modindex generation includes header/footer (storage)"""
        #
        # Ensures that when the extension adds a "modindex" document; any custom
        # defined header/footer data is also injected into the document.

        dataset = os.path.join(self.container, 'sdoc', 'py-modindex')
        footer_tpl = os.path.join(self.template_dir, 'sample-footer.tpl')
        header_tpl = os.path.join(self.template_dir, 'sample-header.tpl')

        config = dict(self.config)
        config['confluence_domain_indices'] = True
        config['confluence_footer_file'] = footer_tpl
        config['confluence_header_file'] = header_tpl

        out_dir = build_sphinx(dataset, config=config)

        with parse('py-modindex', out_dir) as data:
            header_data = data.find().previousSibling.strip()
            self.assertEqual(header_data, 'header content')

            footer_data = data.find_all(recursive=False)[-1].nextSibling.strip()
            self.assertEqual(footer_data, 'footer content')
