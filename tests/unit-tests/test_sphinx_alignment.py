# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceSphinxAlignment(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'alignment'

    @setup_builder('confluence')
    def test_storage_sphinx_alignment_center(self):
        config = dict(self.config)
        config['confluence_default_alignment'] = 'center'

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)
            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'center')

    @setup_builder('confluence')
    def test_storage_sphinx_alignment_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)
            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'center')

    @setup_builder('confluence')
    def test_storage_sphinx_alignment_left(self):
        config = dict(self.config)
        config['confluence_default_alignment'] = 'left'

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)
            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'left')

    @setup_builder('confluence')
    def test_storage_sphinx_alignment_right(self):
        config = dict(self.config)
        config['confluence_default_alignment'] = 'right'

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)
            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'right')
