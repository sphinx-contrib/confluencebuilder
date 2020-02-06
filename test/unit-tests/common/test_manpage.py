# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2018-2020 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
import os
import unittest

class TestConfluenceManpage(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))

        self.config = _.prepareConfiguration()
        self.dataset = os.path.join(test_dir, 'dataset-manpage')
        self.expected = os.path.join(test_dir, 'expected')

    def test_manpage_with_config(self):
        config = dict(self.config)
        config['manpages_url'] = 'https://manpages.example.com/{path}'

        doc_dir, doctree_dir = _.prepareDirectories('manpage-conf')
        app = _.buildSphinx(self.dataset, doc_dir, doctree_dir, config)
        _.assertExpectedWithOutput(
            self, 'manpage-conf', self.expected, doc_dir, tpn='index')

    def test_manpage_without_config(self):
        doc_dir, doctree_dir = _.prepareDirectories('manpage-noconf')
        app = _.buildSphinx(self.dataset, doc_dir, doctree_dir, self.config)
        _.assertExpectedWithOutput(
            self, 'manpage-noconf', self.expected, doc_dir, tpn='index')
