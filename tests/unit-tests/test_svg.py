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
import xml.etree.ElementTree as xml_et


class TestSvg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'svg')

    def _extract_svg_size(self, fname):
        with open(fname, 'rb') as f:
            svg_data = f.read()

        svg_root = xml_et.fromstring(svg_data)
        return int(svg_root.attrib['width']), int(svg_root.attrib['height'])

    def test_storage_svgs(self):
        out_dir = build_sphinx(self.dataset, config=self.config)

        with parse('index', out_dir) as data:
            images = data.find_all('ac:image', recursive=False)
            self.assertEqual(len(images), 10)

            # ##########################################################
            # normal image processing
            # ##########################################################

            image = images.pop(0)

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'svg.svg')
            self.assertFalse(attachment.has_attr('ac:height'))
            self.assertFalse(attachment.has_attr('ac:width'))

            image = images.pop(0)

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'svg-none.svg')
            self.assertFalse(attachment.has_attr('ac:height'))
            self.assertFalse(attachment.has_attr('ac:width'))

            # ##########################################################
            # doctype should be injected into this document
            # ##########################################################

            image = images.pop(0)

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertNotEqual(attachment['ri:filename'], 'svg-doctype.svg')
            self.assertFalse(attachment.has_attr('ac:height'))
            self.assertFalse(attachment.has_attr('ac:width'))

            fname = os.path.join(out_dir, 'svgs', attachment['ri:filename'])
            with open(fname, 'rb') as f:
                svg_data = f.read()
                self.assertTrue(svg_data.lstrip().startswith(b'<?xml'))

            # ##########################################################
            # viewbox sizes into height/width attributes
            # ##########################################################

            image = images.pop(0)

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertNotEqual(attachment['ri:filename'], 'svg-viewbox.svg')
            self.assertFalse(attachment.has_attr('ac:height'))
            self.assertFalse(attachment.has_attr('ac:width'))

            fname = os.path.join(out_dir, 'svgs', attachment['ri:filename'])
            svg_width, svg_height = self._extract_svg_size(fname)
            self.assertEqual(svg_height, 100)
            self.assertEqual(svg_width, 25)

            # ##########################################################
            # applying length/scale options into the svgs
            # ##########################################################

            image = images.pop(0)

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertNotEqual(attachment['ri:filename'], 'svg.svg')
            self.assertFalse(attachment.has_attr('ac:height'))
            self.assertFalse(attachment.has_attr('ac:width'))

            fname = os.path.join(out_dir, 'svgs', attachment['ri:filename'])
            svg_width, svg_height = self._extract_svg_size(fname)
            self.assertEqual(svg_height, 75)
            self.assertEqual(svg_width, 75)

            image = images.pop(0)

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertNotEqual(attachment['ri:filename'], 'svg.svg')
            self.assertFalse(attachment.has_attr('ac:height'))
            self.assertFalse(attachment.has_attr('ac:width'))

            fname = os.path.join(out_dir, 'svgs', attachment['ri:filename'])
            svg_width, svg_height = self._extract_svg_size(fname)
            self.assertEqual(svg_height, 192)
            self.assertEqual(svg_width, 192)

            image = images.pop(0)

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertNotEqual(attachment['ri:filename'], 'svg.svg')
            self.assertFalse(attachment.has_attr('ac:height'))
            self.assertFalse(attachment.has_attr('ac:width'))

            fname = os.path.join(out_dir, 'svgs', attachment['ri:filename'])
            svg_width, svg_height = self._extract_svg_size(fname)
            self.assertEqual(svg_height, 50)
            self.assertEqual(svg_width, 1600)

            image = images.pop(0)

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertNotEqual(attachment['ri:filename'], 'svg.svg')
            self.assertFalse(attachment.has_attr('ac:height'))
            self.assertFalse(attachment.has_attr('ac:width'))

            fname = os.path.join(out_dir, 'svgs', attachment['ri:filename'])
            svg_width, svg_height = self._extract_svg_size(fname)
            self.assertEqual(svg_height, 200)
            self.assertEqual(svg_width, 200)

            # ##########################################################
            # applying length/scale options based on viewbox
            # ##########################################################

            image = images.pop(0)

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertNotEqual(attachment['ri:filename'], 'svg.svg')
            self.assertFalse(attachment.has_attr('ac:height'))
            self.assertFalse(attachment.has_attr('ac:width'))

            fname = os.path.join(out_dir, 'svgs', attachment['ri:filename'])
            svg_width, svg_height = self._extract_svg_size(fname)
            self.assertEqual(svg_height, 200)
            self.assertEqual(svg_width, 50)

            image = images.pop(0)

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertNotEqual(attachment['ri:filename'], 'svg.svg')
            self.assertFalse(attachment.has_attr('ac:height'))
            self.assertFalse(attachment.has_attr('ac:width'))

            fname = os.path.join(out_dir, 'svgs', attachment['ri:filename'])
            svg_width, svg_height = self._extract_svg_size(fname)
            self.assertEqual(svg_height, 200)
            self.assertEqual(svg_width, 50)
