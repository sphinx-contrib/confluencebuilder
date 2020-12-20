# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2018-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import assertExpectedWithOutput
from tests.lib import buildSphinx
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
import os
import unittest

class TestConfluenceManpage(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))

        self.config = prepareConfiguration()
        self.dataset = os.path.join(test_dir, 'dataset-manpage')
        self.expected = os.path.join(test_dir, 'expected')

    def test_legacy_manpage_with_config(self):
        config = dict(self.config)
        config['manpages_url'] = 'https://manpages.example.com/{path}'

        doc_dir, doctree_dir = prepareDirectories('manpage-conf')
        buildSphinx(self.dataset, doc_dir, doctree_dir, config)
        assertExpectedWithOutput(
            self, 'manpage-conf', self.expected, doc_dir, tpn='index')

    def test_legacy_manpage_without_config(self):
        doc_dir, doctree_dir = prepareDirectories('manpage-noconf')
        buildSphinx(self.dataset, doc_dir, doctree_dir, self.config)
        assertExpectedWithOutput(
            self, 'manpage-noconf', self.expected, doc_dir, tpn='index')
