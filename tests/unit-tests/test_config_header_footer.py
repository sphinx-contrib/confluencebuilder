# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceConfigHeaderFooter(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceConfigHeaderFooter, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'common')
        cls.filenames = [
            'header-footer',
        ]

    @setup_builder('confluence')
    def test_storage_config_headerfooter_absolute(self):
        config = dict(self.config)
        footer_tpl = os.path.join(self.templates_dir, 'sample-footer.tpl')
        header_tpl = os.path.join(self.templates_dir, 'sample-header.tpl')
        config['confluence_footer_file'] = footer_tpl
        config['confluence_header_file'] = header_tpl

        out_dir = self.build(self.dataset, config=config,
            filenames=self.filenames)

        with parse('header-footer', out_dir) as data:
            body = data.find('p')
            self.assertIsNotNone(body)
            self.assertEqual(body.text, 'body content')

            header_data = body.previousSibling.strip()
            self.assertEqual(header_data, 'header content')

            footer_data = body.nextSibling.strip()
            self.assertEqual(footer_data, 'footer content')

    @setup_builder('confluence')
    def test_storage_config_headerfooter_relative(self):
        config = dict(self.config)
        config['confluence_footer_file'] = '../../templates/sample-footer.tpl'
        config['confluence_header_file'] = '../../templates/sample-header.tpl'

        out_dir = self.build(self.dataset, config=config,
            filenames=self.filenames)

        with parse('header-footer', out_dir) as data:
            body = data.find('p')
            self.assertIsNotNone(body)
            self.assertEqual(body.text, 'body content')

            header_data = body.previousSibling.strip()
            self.assertEqual(header_data, 'header content')

            footer_data = body.nextSibling.strip()
            self.assertEqual(footer_data, 'footer content')
