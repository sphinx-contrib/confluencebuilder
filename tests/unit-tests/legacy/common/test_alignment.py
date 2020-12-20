# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
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

class TestConfluenceAlignment(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # skip alignment tests pre-sphinx 2.1 as 'default' hints do not exist
        if parse_version(sphinx_version) < parse_version('2.1'):
            raise unittest.SkipTest('default hints not supported in sphinx')

        test_dir = os.path.dirname(os.path.realpath(__file__))

        self.config = prepareConfiguration()
        self.dataset = os.path.join(test_dir, 'dataset-alignment')
        self.expected = os.path.join(test_dir, 'expected')

    def test_legacy_alignment_default(self):
        doc_dir, doctree_dir = prepareDirectories()
        buildSphinx(self.dataset, doc_dir, doctree_dir, self.config)
        assertExpectedWithOutput(
            self, 'alignment-center', self.expected, doc_dir, tpn='index')

    def test_legacy_alignment_left(self):
        config = dict(self.config)
        config['confluence_default_alignment'] = 'left'

        doc_dir, doctree_dir = prepareDirectories()
        buildSphinx(self.dataset, doc_dir, doctree_dir, config)
        assertExpectedWithOutput(
            self, 'alignment-left', self.expected, doc_dir, tpn='index')

    def test_legacy_alignment_center(self):
        config = dict(self.config)
        config['confluence_default_alignment'] = 'center'

        doc_dir, doctree_dir = prepareDirectories()
        buildSphinx(self.dataset, doc_dir, doctree_dir, config)
        assertExpectedWithOutput(
            self, 'alignment-center', self.expected, doc_dir, tpn='index')

    def test_legacy_alignment_right(self):
        config = dict(self.config)
        config['confluence_default_alignment'] = 'right'

        doc_dir, doctree_dir = prepareDirectories()
        buildSphinx(self.dataset, doc_dir, doctree_dir, config)
        assertExpectedWithOutput(
            self, 'alignment-right', self.expected, doc_dir, tpn='index')
