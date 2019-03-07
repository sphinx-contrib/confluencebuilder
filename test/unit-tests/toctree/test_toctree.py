# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017-2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
import os
import unittest

class TestConfluenceToctreeMarkup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = _.prepareConfiguration()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(self.test_dir, 'dataset')

    def test_toctree_child_macro(self):
        config = dict(self.config)
        config['confluence_page_hierarchy'] = True
        config['confluence_adv_hierarchy_child_macro'] = True

        expected = os.path.join(self.test_dir, 'expected-cm')
        doc_dir, doctree_dir = _.prepareDirectories('toctree-markup-cm')
        _.buildSphinx(self.dataset, doc_dir, doctree_dir, config)

        _.assertExpectedWithOutput(self, 'contents', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doca', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'docb', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'docc', expected, doc_dir)

    def test_toctree_default(self):
        expected = os.path.join(self.test_dir, 'expected-def')
        doc_dir, doctree_dir = _.prepareDirectories('toctree-markup-def')
        _.buildSphinx(self.dataset, doc_dir, doctree_dir, self.config)

        _.assertExpectedWithOutput(self, 'contents', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doca', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'docb', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'docc', expected, doc_dir)
