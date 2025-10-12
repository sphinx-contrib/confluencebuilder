# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib.testcase import setup_editor


class TestConfluenceTableWidth(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'table-width'

    @setup_builder('confluence')
    def test_storage_confluence_table_width_default_v1(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            table_tags = data.find_all('table')
            self.assertEqual(len(table_tags), 5)

            # expected no default width
            table_tag = table_tags.pop(0)
            self.assertFalse(table_tag.has_attr('style'))

            # expected 200px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('style'))
            self.assertIn('width: 200px', table_tag['style'])

            # expected no default width
            table_tag = table_tags.pop(0)
            self.assertFalse(table_tag.has_attr('style'))

            # expected 400px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('style'))
            self.assertIn('width: 400px', table_tag['style'])

            # expected no default width
            table_tag = table_tags.pop(0)
            self.assertFalse(table_tag.has_attr('style'))

    @setup_builder('confluence')
    @setup_editor('v2')
    def test_storage_confluence_table_width_default_v2(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            table_tags = data.find_all('table')
            self.assertEqual(len(table_tags), 5)

            # expected no default width
            table_tag = table_tags.pop(0)
            self.assertFalse(table_tag.has_attr('data-table-width'))

            # expected 200px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('data-table-width'))
            self.assertEqual(table_tag['data-table-width'], '200')

            # expected no default width
            table_tag = table_tags.pop(0)
            self.assertFalse(table_tag.has_attr('data-table-width'))

            # expected 400px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('data-table-width'))
            self.assertEqual(table_tag['data-table-width'], '400')

            # expected no default width
            table_tag = table_tags.pop(0)
            self.assertFalse(table_tag.has_attr('data-table-width'))

    @setup_builder('confluence')
    def test_storage_confluence_table_width_set_v1(self):
        config = dict(self.config)
        config['confluence_default_table_width'] = '123'

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            table_tags = data.find_all('table')
            self.assertEqual(len(table_tags), 5)

            # expected 123px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('style'))
            self.assertIn('width: 123px', table_tag['style'])

            # expected 200px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('style'))
            self.assertIn('width: 200px', table_tag['style'])

            # expected 123px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('style'))
            self.assertIn('width: 123px', table_tag['style'])

            # expected 400px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('style'))
            self.assertIn('width: 400px', table_tag['style'])

            # expected 123px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('style'))
            self.assertIn('width: 123px', table_tag['style'])

    @setup_builder('confluence')
    @setup_editor('v2')
    def test_storage_confluence_table_width_set_v2(self):
        config = dict(self.config)
        config['confluence_default_table_width'] = '123'

        out_dir = self.build(self.dataset, config=config)

        with parse('index', out_dir) as data:
            table_tags = data.find_all('table')
            self.assertEqual(len(table_tags), 5)

            # expected 123px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('data-table-width'))
            self.assertEqual(table_tag['data-table-width'], '123')

            # expected 200px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('data-table-width'))
            self.assertEqual(table_tag['data-table-width'], '200')

            # expected 123px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('data-table-width'))
            self.assertEqual(table_tag['data-table-width'], '123')

            # expected 400px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('data-table-width'))
            self.assertEqual(table_tag['data-table-width'], '400')

            # expected 123px width
            table_tag = table_tags.pop(0)
            self.assertTrue(table_tag.has_attr('data-table-width'))
            self.assertEqual(table_tag['data-table-width'], '123')
