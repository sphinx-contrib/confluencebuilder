# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceAssets(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'assets'

    @setup_builder('confluence')
    def test_storage_assets_example(self):
        out_dir = self.build(self.dataset)

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
    def test_storage_assets_no_newline(self):
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
