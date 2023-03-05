# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2016-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceSphinxCodeblockHighlight(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'code-block')

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

            return None
        config['confluence_lang_transform'] = test_override_lang_method

        out_dir = self.build(self.dataset, config=config,
            filenames=['code-block-highlight'])

        with parse('code-block-highlight', out_dir) as data:
            expected = [
                'python',
                'bash',
                'custom-csharp',
                'python',
                'html/xml',
                'python',
            ]

            languages = data.find_all('ac:parameter', {'ac:name': 'language'})
            self._verify_set_languages(languages, expected)

    def _verify_set_languages(self, tags, languages):
        self.assertEqual(len(tags), len(languages))

        for tag, language in zip(tags, languages):
            self.assertEqual(tag.text, language)
