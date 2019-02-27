# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from pkg_resources import parse_version
from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
from sphinx.__init__ import __version__ as sphinx_version
import os
import unittest

class TestConfluenceManpage(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # skip manpages_url tests if not using Sphinx v1.7+
        #
        # https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-manpages_url
        if parse_version(sphinx_version) < parse_version('1.7'):
            raise unittest.SkipTest('manpages_url not supported pre-sphinx-1.7')

        test_dir = os.path.dirname(os.path.realpath(__file__))

        self.config = _.prepareConfiguration()
        self.dataset = os.path.join(test_dir, 'dataset-manpage')
        self.expected = os.path.join(test_dir, 'expected')

    def test_manpage_with_config(self):
        config = dict(self.config)
        config['manpages_url'] = 'https://manpages.example.com/{path}'

        doc_dir, doctree_dir = _.prepareDirectories('manpage-conf')
        app = _.prepareSphinx(self.dataset, doc_dir, doctree_dir, config)
        app.build(force_all=True)
        _.assertExpectedWithOutput(
            self, 'manpage-conf', self.expected, doc_dir, tpn='contents')

    def test_manpage_without_config(self):
        doc_dir, doctree_dir = _.prepareDirectories('manpage-noconf')
        app = _.prepareSphinx(self.dataset, doc_dir, doctree_dir, self.config)
        app.build(force_all=True)
        _.assertExpectedWithOutput(
            self, 'manpage-noconf', self.expected, doc_dir, tpn='contents')
