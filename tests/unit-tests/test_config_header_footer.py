# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceConfigHeaderFooter(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'header-footer'

    @setup_builder('confluence')
    def test_storage_config_headerfooter_absolute(self):
        config = dict(self.config)
        footer_tpl = self.templates_dir / 'sample-footer.tpl'
        header_tpl = self.templates_dir / 'sample-header.tpl'
        config['confluence_footer_file'] = str(footer_tpl)
        config['confluence_header_file'] = str(header_tpl)

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
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

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            body = data.find('p')
            self.assertIsNotNone(body)
            self.assertEqual(body.text, 'body content')

            header_data = body.previousSibling.strip()
            self.assertEqual(header_data, 'header content')

            footer_data = body.nextSibling.strip()
            self.assertEqual(footer_data, 'footer content')

    @setup_builder('confluence')
    def test_storage_config_headerfooter_relative_with_jinja(self):
        config = dict(self.config)
        config['confluence_footer_file'] = '../../templates/sample-footer-with-jinja.tpl'
        config['confluence_header_file'] = '../../templates/sample-header-with-jinja.tpl'
        config['confluence_footer_data'] = {
            'variable': 'footer_value',
        }
        config['confluence_header_data'] = {
            'variable': 'header_value',
        }

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            body = data.find('p')
            self.assertIsNotNone(body)
            self.assertEqual(body.text, 'body content')

            header_data = body.previousSibling.strip()
            self.assertEqual(header_data, 'header content header_value')

            footer_data = body.nextSibling.strip()
            self.assertEqual(footer_data, 'footer content footer_value')
