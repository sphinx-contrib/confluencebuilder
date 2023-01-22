# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2020-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstImage(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'rst', 'image')

    @setup_builder('confluence')
    def test_storage_rst_image_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            images = data.find_all('ac:image', recursive=False)
            self.assertEqual(len(images), 7)

            # ##########################################################
            # external image
            # ##########################################################
            image = images.pop(0)

            url = image.find('ri:url')
            self.assertTrue(url.has_attr('ri:value'))
            self.assertEqual(url['ri:value'],
                'https://www.example.com/image.png')
            self.assertFalse(image.has_attr('ac:align'))

            # ##########################################################
            # external image with options
            # ##########################################################
            image = images.pop(0)

            url = image.find('ri:url')
            raw_url = str(url)
            self.assertTrue(url.has_attr('ri:value'))
            self.assertEqual(url['ri:value'],
                'https://www.example.org/image.png?a=1&b=2')
            self.assertIn('?a=1&amp;b=2', raw_url)
            self.assertFalse(image.has_attr('ac:align'))

            # ##########################################################
            # image with attributes
            # ##########################################################
            image = images.pop(0)

            self.assertTrue(image.has_attr('ac:alt'))
            self.assertEqual(image['ac:alt'], 'alt text')
            self.assertTrue(image.has_attr('ac:width'))
            self.assertEqual(image['ac:width'], '200')
            self.assertFalse(image.has_attr('ac:align'))

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image01.png')

            # ##########################################################
            # image with alignment
            # ##########################################################
            image = images.pop(0)

            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'right')

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image01.png')

            # ##########################################################
            # image with no length units
            # ##########################################################
            image = images.pop(0)

            self.assertTrue(image.has_attr('ac:width'))
            self.assertEqual(image['ac:width'], '123')

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image01.png')

            # ##########################################################
            # image with scaling
            # ##########################################################
            image = images.pop(0)

            self.assertTrue(image.has_attr('ac:width'))
            self.assertEqual(image['ac:width'], '50')

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image01.png')

            # ##########################################################
            # image with non-pixel units
            # ##########################################################
            image = images.pop(0)

            self.assertTrue(image.has_attr('ac:width'))
            self.assertEqual(image['ac:width'], '192')

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image01.png')
