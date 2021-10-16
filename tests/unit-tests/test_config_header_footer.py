# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceConfigHeaderFooter(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.template_dir = os.path.join(test_dir, 'templates')
        self.filenames = [
            'header-footer',
        ]

    def test_storage_config_headerfooter_absolute(self):
        config = dict(self.config)
        footer_tpl = os.path.join(self.template_dir, 'sample-footer.tpl')
        header_tpl = os.path.join(self.template_dir, 'sample-header.tpl')
        config['confluence_footer_file'] = footer_tpl
        config['confluence_header_file'] = header_tpl

        out_dir = build_sphinx(self.dataset, config=config,
            filenames=self.filenames)

        with parse('header-footer', out_dir) as data:
            body = data.find('p')
            self.assertIsNotNone(body)
            self.assertEqual(body.text, 'body content')

            header_data = body.previousSibling.strip()
            self.assertEqual(header_data, 'header content')

            footer_data = body.nextSibling.strip()
            self.assertEqual(footer_data, 'footer content')

    def test_storage_config_headerfooter_relative(self):
        config = dict(self.config)
        config['confluence_footer_file'] = '../../templates/sample-footer.tpl'
        config['confluence_header_file'] = '../../templates/sample-header.tpl'

        out_dir = build_sphinx(self.dataset, config=config,
            filenames=self.filenames)

        with parse('header-footer', out_dir) as data:
            body = data.find('p')
            self.assertIsNotNone(body)
            self.assertEqual(body.text, 'body content')

            header_data = body.previousSibling.strip()
            self.assertEqual(header_data, 'header content')

            footer_data = body.nextSibling.strip()
            self.assertEqual(footer_data, 'footer content')
