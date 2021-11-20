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


class TestConfluenceConfigTitlefix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        cls.config['root_doc'] = 'titlefix'
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'common')
        cls.filenames = [
            'titlefix',
            'titlefix-child',
        ]

    def test_storage_config_titlefix_none(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('titlefix', out_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'],
                'titlefix-child')

        with parse('titlefix-child', out_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'], 'titlefix')

    def test_storage_config_titlefix_postfix(self):
        config = dict(self.config)
        config['confluence_publish_postfix'] = '-mypostfix'

        out_dir = build_sphinx(self.dataset, config=config,
            filenames=self.filenames)

        with parse('titlefix', out_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'],
                'titlefix-child-mypostfix')

        with parse('titlefix-child', out_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'], 'titlefix-mypostfix')

    def test_storage_config_titlefix_prefix(self):
        config = dict(self.config)
        config['confluence_publish_prefix'] = 'myprefix-'

        out_dir = build_sphinx(self.dataset, config=config,
            filenames=self.filenames)

        with parse('titlefix', out_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'],
                'myprefix-titlefix-child')

        with parse('titlefix-child', out_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'], 'myprefix-titlefix')

    def test_storage_config_titlefix_prefix_and_postfix(self):
        config = dict(self.config)
        config['confluence_publish_prefix'] = 'myprefix-'
        config['confluence_publish_postfix'] = '-mypostfix'

        out_dir = build_sphinx(self.dataset, config=config,
            filenames=self.filenames)

        with parse('titlefix', out_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'],
                'myprefix-titlefix-child-mypostfix')

        with parse('titlefix-child', out_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'],
                'myprefix-titlefix-mypostfix')

    def test_storage_config_titlefix_ignore_root(self):
        config = dict(self.config)
        config['confluence_ignore_titlefix_on_index'] = True
        config['confluence_publish_postfix'] = '-mypostfix'
        config['confluence_publish_prefix'] = 'myprefix-'

        out_dir = build_sphinx(self.dataset, config=config,
            filenames=self.filenames)

        with parse('titlefix', out_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'],
                'myprefix-titlefix-child-mypostfix')

        with parse('titlefix-child', out_dir) as data:
            page_ref = data.find('ri:page')
            self.assertIsNotNone(page_ref)
            self.assertEqual(page_ref['ri:content-title'], 'titlefix')
