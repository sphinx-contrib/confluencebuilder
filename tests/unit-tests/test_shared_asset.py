# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceSharedAsset(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'shared-asset')

    def test_storage_sharedasset_defaults(self):
        out_dir = build_sphinx(self.dataset, config=self.config)

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

    def test_storage_sharedasset_force_standalone(self):
        config = dict(self.config)
        config['confluence_asset_force_standalone'] = True
        out_dir = build_sphinx(self.dataset, config=config)

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

    def test_storage_sharedasset_no_newline_assets(self):
        out_dir = build_sphinx(self.dataset, config=self.config)

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
