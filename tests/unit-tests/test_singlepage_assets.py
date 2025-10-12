# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceSinglepageAssets(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'assets'

    @setup_builder('singleconfluence')
    def test_storage_singlepage_asset_defaults(self):
        """validate single page assets are self-contained (storage)"""
        #
        # Ensure when generating a single page that all assets on a page are
        # pointing (implicitly) to itself (i.e. no `ri:page` entry).

        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            images = data.find_all('ac:image')
            self.assertEqual(len(images), 2)

            for image in images:
                attachment = image.find('ri:attachment')
                self.assertIsNotNone(attachment)
                self.assertTrue(attachment.has_attr('ri:filename'))
                self.assertEqual(attachment['ri:filename'], 'image03.png')

                page_ref = attachment.find('ri:page')
                self.assertIsNone(page_ref)

    @setup_builder('singleconfluence')
    def test_storage_singlepage_asset_force_standalone(self):
        """validate single page assets are self-contained alt (storage)"""
        #
        # Ensure when generating a single page that all assets on a page are
        # pointing (implicitly) to itself (i.e. no `ri:page` entry) -- ensure
        # the `confluence_asset_force_standalone` option is not causing issues.

        config = dict(self.config)
        config['confluence_asset_force_standalone'] = True
        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            images = data.find_all('ac:image')
            self.assertEqual(len(images), 2)

            for image in images:
                attachment = image.find('ri:attachment')
                self.assertIsNotNone(attachment)
                self.assertTrue(attachment.has_attr('ri:filename'))
                self.assertEqual(attachment['ri:filename'], 'image03.png')

                page_ref = attachment.find('ri:page')
                self.assertIsNone(page_ref)
