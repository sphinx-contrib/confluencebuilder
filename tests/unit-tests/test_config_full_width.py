# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceConfigFullWidth(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'common')

    @setup_builder('confluence')
    def test_storage_config_full_width_v1_default(self):
        """validate full width modifications for v1 editor (default)"""

        out_dir = self.build(self.dataset, config=self.config)

        with parse('index', out_dir) as data:
            layout = data.find('ac:layout')
            self.assertIsNone(layout)

    @setup_builder('confluence')
    def test_storage_config_full_width_v1_disabled_cloud(self):
        """validate full width modifications for v1 editor (disabled; cloud)"""
        #
        # The use of `confluence_full_width` would typically advise a
        # Confluence instance the layout type on publish. However, this
        # layout management is not supported with a v1 editor. Instead,
        # layout modifications are made to the page's content. This check
        # ensures when configured, these layout options are injected.

        config = dict(self.config)
        config['confluence_full_width'] = False
        config['confluence_server_url'] = \
            'https://sphinxcontrib-confluencebuilder.atlassian.net/wiki/'

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            layout = data.find('ac:layout')
            self.assertIsNotNone(layout)

            section = layout.find('ac:layout-section')
            self.assertIsNotNone(section)
            self.assertTrue(section.has_attr('ac:type'))
            self.assertEqual(section['ac:type'], 'fixed-width')

            cell = section.find('ac:layout-cell')
            self.assertIsNotNone(cell)

    @setup_builder('confluence')
    def test_storage_config_full_width_v1_disabled_dc(self):
        """validate full width modifications for v1 editor (disabled; dc)"""
        #
        # See: test_storage_config_full_width_v1_disabled_cloud
        #
        # This is a variant for non-Cloud versions, which needs an explicit
        # max-width hint.

        config = dict(self.config)
        config['confluence_full_width'] = False

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            container = data.find('div')
            self.assertIsNotNone(container)
            self.assertTrue(container.has_attr('style'))
            self.assertIn('max-width', container['style'])

    @setup_builder('confluence')
    def test_storage_config_full_width_v1_enabled(self):
        """validate full width modifications for v1 editor (enabled)"""

        config = dict(self.config)
        config['confluence_full_width'] = True

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            layout = data.find('ac:layout')
            self.assertIsNone(layout)
