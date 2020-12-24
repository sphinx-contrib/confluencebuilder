# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from pkg_resources import parse_version
from sphinx.__init__ import __version__ as sphinx_version
from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest

class TestConfluenceSphinxCodeblockHighlight(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')

    def test_storage_sphinx_codeblock_linenothreshold(self):
        # skip code-block tests in Sphinx v1.8.x due to regression
        #  https://github.com/sphinx-contrib/confluencebuilder/issues/148
        if parse_version(sphinx_version) < parse_version('2.0'):
            raise unittest.SkipTest('not supported in sphinx-1.8.x')

        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=['code-block-highlight'])

        with parse('code-block-highlight', out_dir) as data:
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
