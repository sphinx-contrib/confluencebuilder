# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import assertExpectedWithOutput
from tests.lib import buildSphinx
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
import os
import unittest

class TestConfluenceToctreeMarkup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepareConfiguration()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_toctree_child_macro(self):
        config = dict(self.config)
        config['confluence_page_hierarchy'] = True
        config['confluence_adv_hierarchy_child_macro'] = True

        dataset = os.path.join(self.test_dir, 'dataset')
        expected = os.path.join(self.test_dir, 'expected-cm')
        doc_dir, doctree_dir = prepareDirectories('toctree-markup-cm')
        buildSphinx(dataset, doc_dir, doctree_dir, config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doca', expected, doc_dir)
        assertExpectedWithOutput(self, 'docb', expected, doc_dir)
        assertExpectedWithOutput(self, 'docc', expected, doc_dir)

    def test_toctree_default(self):
        dataset = os.path.join(self.test_dir, 'dataset')
        expected = os.path.join(self.test_dir, 'expected-def')
        doc_dir, doctree_dir = prepareDirectories('toctree-markup-def')
        buildSphinx(dataset, doc_dir, doctree_dir, self.config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doca', expected, doc_dir)
        assertExpectedWithOutput(self, 'docb', expected, doc_dir)
        assertExpectedWithOutput(self, 'docc', expected, doc_dir)

    def test_toctree_hidden(self):
        dataset = os.path.join(self.test_dir, 'dataset-hidden')
        expected = os.path.join(self.test_dir, 'expected-hidden')
        doc_dir, doctree_dir = prepareDirectories('dataset-hidden')
        buildSphinx(dataset, doc_dir, doctree_dir, self.config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)

    def test_toctree_numbered_default(self):
        config = dict(self.config)
        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered-default')
        doc_dir, doctree_dir = prepareDirectories('toctree-markup-numbered-default')
        buildSphinx(dataset, doc_dir, doctree_dir, config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc2', expected, doc_dir)

    def test_toctree_numbered_disable(self):
        config = dict(self.config)
        config['confluence_add_secnumbers'] = False
        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered-disabled')
        doc_dir, doctree_dir = prepareDirectories('toctree-markup-numbered-disabled')
        buildSphinx(dataset, doc_dir, doctree_dir, config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc2', expected, doc_dir)

    def test_toctree_numbered_secnumbers_suffix(self):
        config = dict(self.config)
        config['confluence_add_secnumbers'] = True
        config['confluence_secnumber_suffix'] = '!Z /+4'
        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered-suffix')
        doc_dir, doctree_dir = prepareDirectories('toctree-markup-numbered-suffix')
        buildSphinx(dataset, doc_dir, doctree_dir, config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc2', expected, doc_dir)

    def test_toctree_numbered_secnumbers_depth(self):
        config = dict(self.config)
        dataset = os.path.join(self.test_dir, 'dataset-numbered-depth')
        expected = os.path.join(self.test_dir, 'expected-numbered-depth')
        doc_dir, doctree_dir = prepareDirectories('toctree-markup-numbered-depth')
        buildSphinx(dataset, doc_dir, doctree_dir, config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc2', expected, doc_dir)
