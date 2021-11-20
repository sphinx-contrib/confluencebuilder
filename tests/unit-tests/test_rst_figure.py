# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_ALIGNMENT
from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceRstFigure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'common')
        cls.filenames = [
            'figure',
        ]

    def test_storage_rst_figure_defaults(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('figure', out_dir) as data:
            figures = data.find_all('ac:structured-macro',
                {'ac:name': 'info'}, recursive=False)
            self.assertEqual(len(figures), 5)

            for figure in figures:
                icon_param = figure.find('ac:parameter',
                    {'ac:name': 'icon'}, recursive=False)
                self.assertIsNotNone(icon_param)
                self.assertEqual(icon_param.text, 'false')

            # ##########################################################
            # external image (default align; no caption)
            # ##########################################################
            figure = figures.pop(0)
            figure_body = figure.find('ac:rich-text-body', recursive=False)
            self.assertIsNotNone(figure_body)

            image = figure_body.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            self.assertTrue(image.has_attr('ac:alt'))
            self.assertEqual(image['ac:alt'], 'alt text')

            url = image.find('ri:url')
            self.assertTrue(url.has_attr('ri:value'))
            self.assertEqual(url['ri:value'],
                'https://www.example.com/image.png')

            if DEFAULT_ALIGNMENT:
                self.assertTrue(image.has_attr('ac:align'))
                self.assertEqual(image['ac:align'], DEFAULT_ALIGNMENT)

            # ##########################################################
            # external image (default align)
            # ##########################################################
            figure = figures.pop(0)
            figure_body = figure.find('ac:rich-text-body', recursive=False)
            self.assertIsNotNone(figure_body)

            image = figure_body.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            self.assertFalse(image.has_attr('ac:alt'))

            url = image.find('ri:url')
            self.assertTrue(url.has_attr('ri:value'))
            self.assertEqual(url['ri:value'],
                'https://www.example.org/image.png')

            caption = figure_body.find('p', recursive=False)
            self.assertIsNotNone(caption)
            self.assertIsNotNone(caption.text, 'caption 2')

            legend = figure_body.find('div', recursive=False)
            self.assertIsNotNone(legend)
            self.assertIsNotNone(legend.text, 'legend 2')

            if DEFAULT_ALIGNMENT:
                self.assertTrue(image.has_attr('ac:align'))
                self.assertEqual(image['ac:align'], DEFAULT_ALIGNMENT)

                css_style = 'text-align: ' + DEFAULT_ALIGNMENT

                self.assertTrue(caption.has_attr('style'))
                self.assertTrue(css_style in caption['style'])

                self.assertTrue(legend.has_attr('style'))
                self.assertTrue(css_style in legend['style'])

            # ##########################################################
            # external image (left align)
            # ##########################################################
            figure = figures.pop(0)
            figure_body = figure.find('ac:rich-text-body', recursive=False)
            self.assertIsNotNone(figure_body)

            image = figure_body.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'left')
            self.assertTrue(image.has_attr('ac:alt'))
            self.assertEqual(image['ac:alt'], 'alt text')

            caption = figure_body.find('p', recursive=False)
            self.assertIsNotNone(caption)
            self.assertIsNotNone(caption.text, 'caption 3')

            legend = figure_body.find('div', recursive=False)
            self.assertIsNotNone(legend)
            self.assertIsNotNone(legend.text, 'legend 3')

            # ##########################################################
            # internal image (center align)
            # ##########################################################
            figure = figures.pop(0)
            figure_body = figure.find('ac:rich-text-body', recursive=False)
            self.assertIsNotNone(figure_body)

            image = figure_body.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'center')

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image02.png')

            caption = figure_body.find('p', recursive=False)
            self.assertIsNotNone(caption)
            self.assertIsNotNone(caption.text, 'caption 4')
            self.assertTrue(caption.has_attr('style'))
            self.assertTrue('text-align: center' in caption['style'])

            legend = figure_body.find('div', recursive=False)
            self.assertIsNotNone(legend)
            self.assertIsNotNone(legend.text, 'legend 4')
            self.assertTrue(legend.has_attr('style'))
            self.assertTrue('text-align: center' in legend['style'])

            # ##########################################################
            # internal image (right align)
            # ##########################################################
            figure = figures.pop(0)
            figure_body = figure.find('ac:rich-text-body', recursive=False)
            self.assertIsNotNone(figure_body)

            image = figure_body.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'right')

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image02.png')

            caption = figure_body.find('p', recursive=False)
            self.assertIsNotNone(caption)
            self.assertIsNotNone(caption.text, 'caption 5')
            self.assertTrue(caption.has_attr('style'))
            self.assertTrue('text-align: right' in caption['style'])

            legend = figure_body.find('div', recursive=False)
            self.assertIsNotNone(legend)
            self.assertIsNotNone(legend.text, 'legend 5')
            self.assertTrue(legend.has_attr('style'))
            self.assertTrue('text-align: right' in legend['style'])

            # ##########################################################

            # ensure each image is followed by a float reset, to ensure any
            # trailing caption/etc. is aligned under the figure's image
            images = data.find_all('ac:image')
            for image in images:
                next_tag = image.find_next_sibling()
                self.assertIsNotNone(next_tag)
                self.assertTrue(next_tag.has_attr('style'))
                self.assertTrue('clear: both' in next_tag['style'])
