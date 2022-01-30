# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from pkg_resources import parse_version
from sphinx.__init__ import __version__ as sphinx_version
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os
import unittest


class TestConfluenceSphinxCodeblockHighlight(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceSphinxCodeblockHighlight, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'common')

    @setup_builder('confluence')
    def test_storage_sphinx_codeblock_highlight_default(self):
        out_dir = self.build(self.dataset,
            filenames=['code-block-highlight'])

        with parse('code-block-highlight', out_dir) as data:
            expected = [
                'python',
                'bash',
                'csharp',
                'python',
                'html/xml',
                'python',
            ]

            languages = data.find_all('ac:parameter', {'ac:name': 'language'})
            self._verify_set_languages(languages, expected)

    @setup_builder('confluence')
    def test_storage_sphinx_codeblock_highlight_linenothreshold(self):
        # skip code-block tests in Sphinx v1.8.x due to regression
        #  https://github.com/sphinx-contrib/confluencebuilder/issues/148
        if parse_version(sphinx_version) < parse_version('2.0'):
            raise unittest.SkipTest('not supported in sphinx-1.8.x')

        out_dir = self.build(self.dataset,
            filenames=['code-block-linenothreshold'])

        with parse('code-block-linenothreshold', out_dir) as data:
            code_macros = data.find_all('ac:structured-macro',
                {'ac:name': 'code'})
            self.assertIsNotNone(code_macros)
            self.assertEqual(len(code_macros), 2)

            for code_macro in code_macros:
                self.assertTrue(code_macro.has_attr('ac:name'))
                self.assertEqual(code_macro['ac:name'], 'code')

            # no lines block under `linenothreshold` count
            block = code_macros.pop(0)
            linenumbers = block.find('ac:parameter',
                {'ac:name': 'linenumbers'})
            self.assertIsNotNone(linenumbers)
            self.assertEqual(linenumbers.text, 'false')

            # with lines block under `linenothreshold` count
            block = code_macros.pop(0)
            linenumbers = block.find('ac:parameter',
                {'ac:name': 'linenumbers'})
            self.assertIsNotNone(linenumbers)
            self.assertEqual(linenumbers.text, 'true')

    @setup_builder('confluence')
    def test_storage_sphinx_codeblock_highlight_none(self):
        config = dict(self.config)
        config['highlight_language'] = 'none'

        out_dir = self.build(self.dataset, config=config,
            filenames=['code-block-highlight'])

        with parse('code-block-highlight', out_dir) as data:
            expected = [
                'none',
                'bash',
                'csharp',
                'python',
                'html/xml',
                'python',
            ]

            languages = data.find_all('ac:parameter', {'ac:name': 'language'})
            self._verify_set_languages(languages, expected)

    @setup_builder('confluence')
    def test_storage_sphinx_codeblock_highlight_override(self):
        config = dict(self.config)

        def test_override_lang_method(lang):
            if lang == 'csharp':
                return 'custom-csharp'

            return 'custom'
        config['confluence_lang_transform'] = test_override_lang_method

        out_dir = self.build(self.dataset, config=config,
            filenames=['code-block-highlight'])

        with parse('code-block-highlight', out_dir) as data:
            expected = [
                'custom',
                'custom',
                'custom-csharp',
                'custom',
                'custom',
                'custom',
            ]

            languages = data.find_all('ac:parameter', {'ac:name': 'language'})
            self._verify_set_languages(languages, expected)

    def _verify_set_languages(self, tags, languages):
        self.assertEqual(len(tags), len(languages))

        for tag, language in zip(tags, languages):
            self.assertEqual(tag.text, language)
