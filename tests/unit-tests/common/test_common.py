# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.std.sphinx import DEFAULT_ALIGNMENT
from tests.lib import EXT_NAME
from tests.lib import assertExpectedWithOutput
from tests.lib import parse
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
from tests.lib import prepareSphinx
import os
import unittest

class TestConfluenceCommon(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepareConfiguration()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        dataset = os.path.join(test_dir, 'dataset-common')
        self.expected = os.path.join(test_dir, 'expected')

        doc_dir, doctree_dir = prepareDirectories('common')
        self.doc_dir = doc_dir

        with prepareSphinx(dataset, doc_dir, doctree_dir, self.config) as app:
            app.build(force_all=True)

            # track registered extensions
            if hasattr(app, 'extensions'):
                self.extensions = list(app.extensions.keys())
            else:
                self.extensions = list(app._extensions.keys())

    def _assertExpectedWithOutput(self, name, expected=None):
        expected = expected if expected else self.expected
        assertExpectedWithOutput(self, name, expected, self.doc_dir)

    def test_failure(self):
            self.assertEqual(False, True)

    def test_admonitions(self):
        def verify_admonition_tags(data, text, expected_type):
            leaf = data.find(text=text)
            self.assertIsNotNone(leaf,
                'unable to find target admonition ' + text)

            expected_para = leaf.parent
            self.assertEqual(expected_para.name, 'p',
                'admonition ' + text + ' text not wrapped in a paragraph')

            expected_rich_txt_body = expected_para.parent
            self.assertEqual(expected_rich_txt_body.name, 'ac:rich-text-body',
                'admonition ' + text + ' context not using rich-text-body')

            expected_macro = expected_rich_txt_body.parent
            self.assertEqual(expected_macro.name, 'ac:structured-macro',
                'admonition ' + text + ' not contained inside a macro')

            self.assertEqual(expected_macro['ac:name'], expected_type,
                'admonition ' + text + ' not contained inside a macro')

            return expected_macro

        with parse('admonitions', self.doc_dir) as data:
            verify_admonition_tags(data, 'attention', 'note')
            verify_admonition_tags(data, 'caution', 'note')
            verify_admonition_tags(data, 'danger', 'warning')
            verify_admonition_tags(data, 'error', 'warning')
            verify_admonition_tags(data, 'hint', 'tip')
            verify_admonition_tags(data, 'important', 'warning')
            verify_admonition_tags(data, 'note', 'info')
            verify_admonition_tags(data, 'tip', 'tip')
            verify_admonition_tags(data, 'warning', 'warning')

            macro = verify_admonition_tags(data, 'admonition', 'info')
            title_param = macro.find('ac:parameter', {'ac:name': 'title'})
            self.assertIsNotNone(title_param,
                'admonition is missing a title paramater')
            self.assertEqual(title_param.text, 'title',
                'admonition title value does not match expected')
            icon_param = macro.find('ac:parameter', {'ac:name': 'icon'})
            self.assertIsNotNone(icon_param,
                'admonition is missing a icon paramater')
            self.assertEqual(icon_param.text, 'false',
                'admonition icon value is not disabled')

    def test_attribution(self):
        self._assertExpectedWithOutput('attribution')

    def test_bibliographic(self):
        self._assertExpectedWithOutput('bibliographic')

    def test_block_quotes(self):
        self._assertExpectedWithOutput('block-quotes')

    def test_citations(self):
        self._assertExpectedWithOutput('citations')

    def test_contents(self):
        self._assertExpectedWithOutput('contents')

    def test_definition_lists(self):
        self._assertExpectedWithOutput('definition-lists')

    def test_deprecated(self):
        self._assertExpectedWithOutput('deprecated')

    def test_download(self):
        self._assertExpectedWithOutput('download')

    def test_epigraph(self):
        self._assertExpectedWithOutput('epigraph')

    def test_figure(self):
        if DEFAULT_ALIGNMENT == 'center':
            expected = self.expected + '-center'
            self._assertExpectedWithOutput('figure', expected)
        else:
            self._assertExpectedWithOutput('figure')

    def test_footnotes(self):
        self._assertExpectedWithOutput('footnotes')

    def test_glossary(self):
        self._assertExpectedWithOutput('glossary')
        self._assertExpectedWithOutput('glossary-ref')

    def test_image(self):
        self._assertExpectedWithOutput('image')

    def test_index(self):
        self._assertExpectedWithOutput('index')

    def test_lists(self):
        self._assertExpectedWithOutput('lists')

    def test_list_table(self):
        self._assertExpectedWithOutput('list-table')

    def test_markup(self):
        self._assertExpectedWithOutput('markup')

    def test_option_lists(self):
        self._assertExpectedWithOutput('option-lists')

    def test_parsed_literal(self):
        self._assertExpectedWithOutput('parsed-literal')

    def test_production_list(self):
        self._assertExpectedWithOutput('production-list')

    def test_raw(self):
        self._assertExpectedWithOutput('raw')

    def test_references(self):
        self._assertExpectedWithOutput('references')
        self._assertExpectedWithOutput('references-ref')

    def test_registry(self):
        # validate builder's registration into Sphinx
        self.assertTrue(EXT_NAME in self.extensions)

    def test_sections(self):
        self._assertExpectedWithOutput('sections')

    def test_table(self):
        self._assertExpectedWithOutput('tables')

    def test_transitions(self):
        self._assertExpectedWithOutput('transitions')
