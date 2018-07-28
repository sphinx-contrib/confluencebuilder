# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2018 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinx.application import Sphinx
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
import os
import unittest

from pkg_resources import iter_entry_points

class TestConfluenceCommonHeadings(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))

        self.config = _.prepareConfiguration()
        self.dataset = os.path.join(test_dir, 'dataset-headings')
        self.expected = os.path.join(test_dir, 'expected')

    def test_headings_default(self):
        doc_dir, doctree_dir = _.prepareDirectories('headings-default')
        app = _.prepareSphinx(self.dataset, doc_dir, doctree_dir, self.config)
        app.build(force_all=True)
        _.assertExpectedWithOutput(
            self, 'headings-default', self.expected, doc_dir, tpn='headings')

    def test_headings_with_title(self):
        config = dict(self.config)
        config['confluence_remove_title'] = False

        doc_dir, doctree_dir = _.prepareDirectories('headings-with-title')
        app = _.prepareSphinx(self.dataset, doc_dir, doctree_dir, config)
        app.build(force_all=True)
        _.assertExpectedWithOutput(
            self, 'headings-with-title', self.expected, doc_dir, tpn='headings')
