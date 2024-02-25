# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_ALIGNMENT
from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib.testcase import setup_editor


class TestConfluenceRstFigure(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'figure'

    @setup_builder('confluence')
    def test_storage_rst_figure_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            figures = data.find_all('p', recursive=False)
            self.assertEqual(len(figures), 5)

            # ##########################################################
            # external image (default align; no caption)
            # ##########################################################
            figure = figures.pop(0)

            image = figure.find('ac:image', recursive=False)
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

            image = figure.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            self.assertFalse(image.has_attr('ac:alt'))

            url = image.find('ri:url')
            self.assertTrue(url.has_attr('ri:value'))
            self.assertEqual(url['ri:value'],
                'https://www.example.org/image.png')

            caption = figure.find('p', recursive=False)
            self.assertIsNotNone(caption)
            self.assertIsNotNone(caption.text, 'caption 2')

            legend = figure.find('div', recursive=False)
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

            image = figure.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'left')
            self.assertTrue(image.has_attr('ac:alt'))
            self.assertEqual(image['ac:alt'], 'alt text')

            caption = figure.find('p', recursive=False)
            self.assertIsNotNone(caption)
            self.assertIsNotNone(caption.text, 'caption 3')

            legend = figure.find('div', recursive=False)
            self.assertIsNotNone(legend)
            self.assertIsNotNone(legend.text, 'legend 3')

            # ##########################################################
            # internal image (center align)
            # ##########################################################
            figure = figures.pop(0)

            image = figure.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'center')

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image02.png')

            caption = figure.find('p', recursive=False)
            self.assertIsNotNone(caption)
            self.assertIsNotNone(caption.text, 'caption 4')
            self.assertTrue(caption.has_attr('style'))
            self.assertTrue('text-align: center' in caption['style'])

            legend = figure.find('div', recursive=False)
            self.assertIsNotNone(legend)
            self.assertIsNotNone(legend.text, 'legend 4')
            self.assertTrue(legend.has_attr('style'))
            self.assertTrue('text-align: center' in legend['style'])

            # ##########################################################
            # internal image (right align)
            # ##########################################################
            figure = figures.pop(0)

            image = figure.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'right')

            attachment = image.find('ri:attachment')
            self.assertTrue(attachment.has_attr('ri:filename'))
            self.assertEqual(attachment['ri:filename'], 'image02.png')

            caption = figure.find('p', recursive=False)
            self.assertIsNotNone(caption)
            self.assertIsNotNone(caption.text, 'caption 5')
            self.assertTrue(caption.has_attr('style'))
            self.assertTrue('text-align: right' in caption['style'])

            legend = figure.find('div', recursive=False)
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
                if not next_tag:
                    next_tag = image.parent.find_next_sibling()

                self.assertIsNotNone(next_tag)
                self.assertTrue(next_tag.has_attr('style'))
                self.assertTrue('clear: both' in next_tag['style'])

    @setup_builder('confluence')
    def test_storage_rst_figure_caption_default(self):
        dataset = self.datasets / 'rst' / 'figure-caption'
        out_dir = self.build(dataset)

        with parse('index', out_dir) as data:
            figures = data.find_all('p', recursive=False)
            self.assertEqual(len(figures), 1)

            # ##########################################################
            # single figure with caption
            # ##########################################################
            figure = figures.pop(0)

            image = figure.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            caption = figure.find('p', recursive=False)
            self.assertIsNotNone(caption)

            markup1 = caption.find('strong', recursive=False)
            self.assertIsNotNone(markup1)
            self.assertIsNotNone(markup1.text, 'caption')

            markup2 = caption.find('em', recursive=False)
            self.assertIsNotNone(markup2)
            self.assertIsNotNone(markup2.text, 'markup')

    @setup_builder('confluence')
    @setup_editor('v2')
    def test_storage_rst_figure_caption_v2(self):
        dataset = self.datasets / 'rst' / 'figure-caption'
        out_dir = self.build(dataset)

        with parse('index', out_dir) as data:
            figures = data.find_all('p', recursive=False)
            self.assertEqual(len(figures), 1)

            # ##########################################################
            # single figure with caption
            # ##########################################################
            figure = figures.pop(0)

            image = figure.find('ac:image', recursive=False)
            self.assertIsNotNone(image)

            caption = image.find('ac:caption', recursive=False)
            self.assertIsNotNone(caption)

            markup1 = caption.find('strong', recursive=False)
            self.assertIsNotNone(markup1)
            self.assertIsNotNone(markup1.text, 'caption')

            markup2 = caption.find('em', recursive=False)
            self.assertIsNotNone(markup2)
            self.assertIsNotNone(markup2.text, 'markup')
