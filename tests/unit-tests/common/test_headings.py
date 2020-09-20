# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.application import Sphinx
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from tests.lib import assertExpectedWithOutput
from tests.lib import buildSphinx
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
import os
import unittest

class TestConfluenceCommonHeadings(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))

        self.config = prepareConfiguration()
        self.dataset = os.path.join(test_dir, 'dataset-headings')
        self.expected = os.path.join(test_dir, 'expected')

    def test_headings_default(self):
        doc_dir, doctree_dir = prepareDirectories('headings-default')
        app = buildSphinx(self.dataset, doc_dir, doctree_dir, self.config)
        assertExpectedWithOutput(
            self, 'headings-default', self.expected, doc_dir, tpn='headings')

    def test_headings_with_title(self):
        config = dict(self.config)
        config['confluence_remove_title'] = False

        doc_dir, doctree_dir = prepareDirectories('headings-with-title')
        app = buildSphinx(self.dataset, doc_dir, doctree_dir, config)
        assertExpectedWithOutput(
            self, 'headings-with-title', self.expected, doc_dir, tpn='headings')
