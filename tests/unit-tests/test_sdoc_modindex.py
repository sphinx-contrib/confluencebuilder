# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestSdocModindex(ConfluenceTestCase):
    @setup_builder('confluence')
    def test_sdoc_modindex_default_missing_confluence(self):
        """validate modindex is not added by default (storage)"""

        dataset = self.datasets / 'minimal'

        out_dir = self.build(dataset)

        fname_check = out_dir / 'py-modindex.conf'
        self.assertFalse(fname_check.is_file())

    @setup_builder('singleconfluence')
    def test_sdoc_modindex_default_missing_singleconfluence(self):
        """validate modindex is not added by default (storage)"""

        dataset = self.datasets / 'minimal'

        out_dir = self.build(dataset)

        fname_check = out_dir / 'py-modindex.conf'
        self.assertFalse(fname_check.is_file())

    @setup_builder('confluence')
    def test_storage_sdoc_modindex_enabled(self):
        """validate modindex generation can be enabled (storage)"""
        #
        # Ensures the extension adds a "py-modindex" document when the domain
        # indices option is assigned to include the domain type.

        dataset = self.datasets / 'sdoc' / 'py-modindex'
        config = dict(self.config)
        config['confluence_domain_indices'] = [
            'py-modindex',
        ]

        out_dir = self.build(dataset, config=config)

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

    @setup_builder('confluence')
    def test_storage_sdoc_modindex_enabled_bool(self):
        """validate modindex generation can be bool-enabled (storage)"""
        #
        # Ensures the extension adds a "py-modindex" document when the domain
        # indices option is assigned to a `True` value.

        dataset = self.datasets / 'sdoc' / 'py-modindex'
        config = dict(self.config)
        config['confluence_domain_indices'] = True

        out_dir = self.build(dataset, config=config)

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

    @setup_builder('confluence')
    def test_storage_sdoc_modindex_header_footer(self):
        """validate modindex generation includes header/footer (storage)"""
        #
        # Ensures that when the extension adds a "modindex" document; any custom
        # defined header/footer data is also injected into the document.

        dataset = self.datasets / 'sdoc' / 'py-modindex'
        footer_tpl = self.templates_dir / 'sample-footer.tpl'
        header_tpl = self.templates_dir / 'sample-header.tpl'

        config = dict(self.config)
        config['confluence_domain_indices'] = True
        config['confluence_footer_file'] = footer_tpl
        config['confluence_header_file'] = header_tpl

        out_dir = self.build(dataset, config=config)

        with parse('py-modindex', out_dir) as data:
            header_data = data.find().previousSibling.strip()
            self.assertEqual(header_data, 'header content')

            footer_data = data.find_all(recursive=False)[-1].nextSibling.strip()
            self.assertEqual(footer_data, 'footer content')
