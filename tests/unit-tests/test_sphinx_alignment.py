# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from pkg_resources import parse_version
from sphinx.__init__ import __version__ as sphinx_version
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os
import unittest


class TestConfluenceSphinxAlignment(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceSphinxAlignment, cls).setUpClass()

        # skip alignment tests pre-sphinx 2.1 as 'default' hints do not exist
        if parse_version(sphinx_version) < parse_version('2.1'):
            raise unittest.SkipTest('default hints not supported in sphinx')

        cls.dataset = os.path.join(cls.datasets, 'common')
        cls.filenames = [
            'alignment',
        ]

    @setup_builder('confluence')
    def test_storage_sphinx_alignment_center(self):
        config = dict(self.config)
        config['confluence_default_alignment'] = 'center'

        out_dir = self.build(self.dataset, config=config,
            filenames=self.filenames)

        with parse('alignment', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)
            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'center')

    @setup_builder('confluence')
    def test_storage_sphinx_alignment_default(self):
        out_dir = self.build(self.dataset, filenames=self.filenames)

        with parse('alignment', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)
            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'center')

    @setup_builder('confluence')
    def test_storage_sphinx_alignment_left(self):
        config = dict(self.config)
        config['confluence_default_alignment'] = 'left'

        out_dir = self.build(self.dataset, config=config,
            filenames=self.filenames)

        with parse('alignment', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)
            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'left')

    @setup_builder('confluence')
    def test_storage_sphinx_alignment_right(self):
        config = dict(self.config)
        config['confluence_default_alignment'] = 'right'

        out_dir = self.build(self.dataset, config=config,
            filenames=self.filenames)

        with parse('alignment', out_dir) as data:
            image = data.find('ac:image')
            self.assertIsNotNone(image)
            self.assertTrue(image.has_attr('ac:align'))
            self.assertEqual(image['ac:align'], 'right')
