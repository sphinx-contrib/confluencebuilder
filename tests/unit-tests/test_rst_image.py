# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceRstImage(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'image',
        ]

    def test_storage_rst_image_defaults(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('image', out_dir) as data:
            images = data.find_all('ac:image', recursive=False)
            self.assertEqual(len(images), 3)

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
            self.assertEqual(image['ac:width'], '200px')
            self.assertFalse(image.has_attr('ac:align'))

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image01.png')

            # ##########################################################
            # image with alignment and scaling
            # ##########################################################
            image = images.pop(0)

            self.assertTrue(image.has_attr('ac:width'))
            self.assertIsNotNone(image['ac:width'])
            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'right')

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image01.png')
