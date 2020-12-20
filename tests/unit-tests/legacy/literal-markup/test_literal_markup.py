# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from pkg_resources import parse_version
from sphinx.__init__ import __version__ as sphinx_version
from tests.lib import assertExpectedWithOutput
from tests.lib import buildSphinx
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
import os
import unittest

class TestConfluenceLiteralMarkup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepareConfiguration()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        dataset = os.path.join(test_dir, 'dataset')
        self.expected = os.path.join(test_dir, 'expected')

        doc_dir = prepareDirectories('literal-markup')
        buildSphinx(dataset, config=self.config, out_dir=doc_dir)

        self.doc_dir = doc_dir

    def test_legacy_code_blocks(self):
        # skip code-block tests in Sphinx v1.8.x due to regression
        #  https://github.com/sphinx-contrib/confluencebuilder/issues/148
        if parse_version(sphinx_version) < parse_version('2.0'):
            raise unittest.SkipTest('not supported in sphinx-1.8.x')
        assertExpectedWithOutput(
            self, 'code_blocks', self.expected, self.doc_dir)

    def test_legacy_literal_blocks(self):
        assertExpectedWithOutput(
            self, 'literal_blocks', self.expected, self.doc_dir)

    def test_legacy_literal_includes(self):
        assertExpectedWithOutput(
            self, 'literal_includes', self.expected, self.doc_dir)
