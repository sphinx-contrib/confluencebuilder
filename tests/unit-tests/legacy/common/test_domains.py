# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2019-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from pkg_resources import parse_version
from sphinx.__init__ import __version__ as sphinx_version
from tests.lib import assertExpectedWithOutput
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
from tests.lib import prepareSphinx
import os
import unittest

class TestConfluenceDomains(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        config = prepareConfiguration()
        config['confluence_adv_restricted'] = ['anchor']
        test_dir = os.path.dirname(os.path.realpath(__file__))
        dataset = os.path.join(test_dir, 'dataset-domains')
        self.expected = os.path.join(test_dir, 'expected-domains')

        doc_dir = prepareDirectories('domains')
        self.doc_dir = doc_dir

        with prepareSphinx(dataset, doc_dir, config) as app:
            app.build(force_all=True)

    def _assertExpectedWithOutput(self, name, expected=None):
        expected = expected if expected else self.expected
        assertExpectedWithOutput(self, name, expected, self.doc_dir)

    def test_legacy_domains_c(self):
        if parse_version(sphinx_version) >= parse_version('3.0'):
            self._assertExpectedWithOutput('c')
        else:
            # pre-v3.0 left-aligns pointer asterisk and embeds in variable
            expected = self.expected + '-legacy'
            self._assertExpectedWithOutput('c', expected)

    def test_legacy_domains_cpp(self):
        self._assertExpectedWithOutput('cpp')

    def test_legacy_domains_js(self):
        self._assertExpectedWithOutput('js')

    def test_legacy_domains_py(self):
        self._assertExpectedWithOutput('py')

    def test_legacy_domains_rst(self):
        self._assertExpectedWithOutput('rst')
