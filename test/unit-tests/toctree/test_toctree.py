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

    def test_toctree_child_macro(self):
        config = dict(self.config)
        config['confluence_page_hierarchy'] = True
        config['confluence_adv_hierarchy_child_macro'] = True

        dataset = os.path.join(self.test_dir, 'dataset')
        expected = os.path.join(self.test_dir, 'expected-cm')
        doc_dir, doctree_dir = _.prepareDirectories('toctree-markup-cm')
        _.buildSphinx(dataset, doc_dir, doctree_dir, config)

        _.assertExpectedWithOutput(self, 'index', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doca', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'docb', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'docc', expected, doc_dir)

    def test_toctree_default(self):
        dataset = os.path.join(self.test_dir, 'dataset')
        expected = os.path.join(self.test_dir, 'expected-def')
        doc_dir, doctree_dir = _.prepareDirectories('toctree-markup-def')
        _.buildSphinx(dataset, doc_dir, doctree_dir, self.config)

        _.assertExpectedWithOutput(self, 'index', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doca', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'docb', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'docc', expected, doc_dir)

    def test_toctree_hidden(self):
        dataset = os.path.join(self.test_dir, 'dataset-hidden')
        expected = os.path.join(self.test_dir, 'expected-hidden')
        doc_dir, doctree_dir = _.prepareDirectories('dataset-hidden')
        _.buildSphinx(dataset, doc_dir, doctree_dir, self.config)

        _.assertExpectedWithOutput(self, 'index', expected, doc_dir)

    def test_toctree_numbered_default(self):
        config = dict(self.config)
        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered-default')
        doc_dir, doctree_dir = _.prepareDirectories('toctree-markup-numbered-default')
        _.buildSphinx(dataset, doc_dir, doctree_dir, config)

        _.assertExpectedWithOutput(self, 'index', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doc2', expected, doc_dir)

    def test_toctree_numbered_disable(self):
        config = dict(self.config)
        config['confluence_add_secnumbers'] = False
        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered-disabled')
        doc_dir, doctree_dir = _.prepareDirectories('toctree-markup-numbered-disabled')
        _.buildSphinx(dataset, doc_dir, doctree_dir, config)

        _.assertExpectedWithOutput(self, 'index', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doc2', expected, doc_dir)

    def test_toctree_numbered_secnumbers_suffix(self):
        config = dict(self.config)
        config['confluence_add_secnumbers'] = True
        config['confluence_secnumber_suffix'] = '!Z /+4'
        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered-suffix')
        doc_dir, doctree_dir = _.prepareDirectories('toctree-markup-numbered-suffix')
        _.buildSphinx(dataset, doc_dir, doctree_dir, config)

        _.assertExpectedWithOutput(self, 'index', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doc2', expected, doc_dir)

    def test_toctree_numbered_secnumbers_depth(self):
        config = dict(self.config)
        dataset = os.path.join(self.test_dir, 'dataset-numbered-depth')
        expected = os.path.join(self.test_dir, 'expected-numbered-depth')
        doc_dir, doctree_dir = _.prepareDirectories('toctree-markup-numbered-depth')
        _.buildSphinx(dataset, doc_dir, doctree_dir, config)

        _.assertExpectedWithOutput(self, 'index', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        _.assertExpectedWithOutput(self, 'doc2', expected, doc_dir)
