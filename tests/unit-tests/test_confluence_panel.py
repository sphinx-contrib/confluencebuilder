# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinx.errors import SphinxWarning
from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluencePanel(ConfluenceTestCase):
    @setup_builder('confluence')
    def test_storage_confluence_panel_directive_expected(self):
        out_dir = self.build(self.datasets / 'panel')

        with parse('index', out_dir) as data:
            panel_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'panel'})
            self.assertIsNotNone(panel_macros)
            self.assertEqual(len(panel_macros), 8)

            # panel macro without no options
            panel_macro = panel_macros.pop(0)

            rich_body = panel_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            parameters = panel_macro.find('ac:parameter')
            self.assertIsNone(parameters)

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'plain content')

            # panel macro with background color
            panel_macro = panel_macros.pop(0)

            rich_body = panel_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            bg_color = panel_macro.find('ac:parameter', {'ac:name': 'bgColor'})
            self.assertIsNotNone(bg_color)
            self.assertEqual(bg_color.text, '#ee0000')

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'with background color')

            # panel macro with border color
            panel_macro = panel_macros.pop(0)

            rich_body = panel_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            border_color = panel_macro.find('ac:parameter',
                {'ac:name': 'borderColor'})
            self.assertIsNotNone(border_color)
            self.assertEqual(border_color.text, '#00ee00')

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'with border color')

            # panel macro with border style
            panel_macro = panel_macros.pop(0)

            rich_body = panel_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            border_style = panel_macro.find('ac:parameter',
                {'ac:name': 'borderStyle'})
            self.assertIsNotNone(border_style)
            self.assertEqual(border_style.text, 'dashed')

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'with border style')

            # panel macro border width content
            panel_macro = panel_macros.pop(0)

            rich_body = panel_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            border_style = panel_macro.find('ac:parameter',
                {'ac:name': 'borderWidth'})
            self.assertIsNotNone(border_style)
            self.assertEqual(border_style.text, '12')

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'with border width content')

            # panel macro with a title
            panel_macro = panel_macros.pop(0)

            rich_body = panel_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            title = panel_macro.find('ac:parameter', {'ac:name': 'title'})
            self.assertIsNotNone(title)
            self.assertEqual(title.text, 'my title')

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'with title content')

            # panel macro with title background color
            panel_macro = panel_macros.pop(0)

            rich_body = panel_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            title_bg_color = panel_macro.find('ac:parameter',
                {'ac:name': 'titleBGColor'})
            self.assertIsNotNone(title_bg_color)
            self.assertEqual(title_bg_color.text, '#0000ee')

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'with title background color')

            # panel macro title color
            panel_macro = panel_macros.pop(0)

            rich_body = panel_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            title_color = panel_macro.find('ac:parameter',
                {'ac:name': 'titleColor'})
            self.assertIsNotNone(title_color)
            self.assertEqual(title_color.text, '#ee00ee')

            contents = rich_body.text.strip()
            self.assertIsNotNone(contents)
            self.assertEqual(contents, 'with title color')

    @setup_builder('confluence')
    def test_storage_confluence_panel_directive_missing_title_bgcolor(self):
        with self.assertRaises(SphinxWarning):
            self.build(
                self.datasets / 'panel-missing-title-with-title-bg-color')

    @setup_builder('confluence')
    def test_storage_confluence_panel_directive_missing_title_color(self):
        with self.assertRaises(SphinxWarning):
            self.build(
                self.datasets / 'panel-missing-title-with-title-color')
