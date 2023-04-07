# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceSharedAsset(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'shared-asset')

    @setup_builder('confluence')
    def test_storage_sharedasset_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('doc-a', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)

            attachment = image.find('ri:attachment')
            self.assertIsNotNone(attachment)
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image03.png')

            page_ref = attachment.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'shared asset')

        with parse('doc-b', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)

            attachment = image.find('ri:attachment')
            self.assertIsNotNone(attachment)
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image03.png')

            page_ref = attachment.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertTrue(page_ref.has_attr('ri:content-title'))
            self.assertEqual(page_ref['ri:content-title'], 'shared asset')

    @setup_builder('confluence')
    def test_storage_sharedasset_force_standalone(self):
        config = dict(self.config)
        config['confluence_asset_force_standalone'] = True
        out_dir = self.build(self.dataset, config=config)

        with parse('doc-a', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)

            attachment = image.find('ri:attachment')
            self.assertIsNotNone(attachment)
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image03.png')

            page_ref = attachment.find('ri:page')
            self.assertIsNone(page_ref)

        with parse('doc-b', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)

            attachment = image.find('ri:attachment')
            self.assertIsNotNone(attachment)
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image03.png')

            page_ref = attachment.find('ri:page')
            self.assertIsNone(page_ref)

    @setup_builder('confluence')
    def test_storage_sharedasset_no_newline_assets(self):
        out_dir = self.build(self.dataset)

        # confluence (error 500) attachment newline check
        #
        # Attachment text cannot have a newline, or Confluence may throw a
        # 500 error when publishing a document.
        with parse('doc-a', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)

            attachment = image.find('ri:attachment')
            self.assertIsNotNone(attachment)
            self.assertFalse('\n' in attachment.text)
