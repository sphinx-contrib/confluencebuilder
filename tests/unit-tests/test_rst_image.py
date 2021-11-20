# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceRstImage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'common')
        cls.filenames = [
            'image',
        ]

    def test_storage_rst_image_defaults(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('image', out_dir) as data:
            images = data.find_all('ac:image', recursive=False)
            self.assertEqual(len(images), 6)

            # ##########################################################
            # basic image
            # ##########################################################
            image = images.pop(0)

            url = image.find('ri:url')
            self.assertTrue(url.has_attr('ri:value'))
            self.assertEqual(url['ri:value'],
                'https://www.example.com/image.png')
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
