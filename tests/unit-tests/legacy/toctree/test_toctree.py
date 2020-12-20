# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import assertExpectedWithOutput
from tests.lib import buildSphinx
from tests.lib import parse
from tests.lib import prepareConfiguration
import os
import unittest

class TestConfluenceToctreeMarkup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepareConfiguration()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_legacy_contents_default(self):
        dataset = os.path.join(self.test_dir, 'dataset-contents')
        doc_dir = buildSphinx(dataset, config=self.config)

        with parse('sub', doc_dir) as data:
            top_link = data.find('a')
            self.assertIsNotNone(top_link, 'unable to find first link tag (a)')
            self.assertEqual(top_link['href'], '#top',
                'contents root document not a top reference')

    def test_legacy_contents_with_title(self):
        config = dict(self.config)
        config['confluence_remove_title'] = False

        dataset = os.path.join(self.test_dir, 'dataset-contents')
        doc_dir = buildSphinx(dataset, config=config)

        with parse('sub', doc_dir) as data:
            top_link = data.find('ac:link')
            self.assertIsNotNone(top_link,
                'unable to find first link tag (ac:link)')
            self.assertEqual(top_link['ac:anchor'], '1. sub',
                'contents root document has an unexpected anchor value')

    def test_legacy_toctree_child_macro(self):
        config = dict(self.config)
        config['confluence_page_hierarchy'] = True
        config['confluence_adv_hierarchy_child_macro'] = True

        dataset = os.path.join(self.test_dir, 'dataset')
        expected = os.path.join(self.test_dir, 'expected-cm')
        doc_dir = buildSphinx(dataset, config=config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doca', expected, doc_dir)
        assertExpectedWithOutput(self, 'docb', expected, doc_dir)
        assertExpectedWithOutput(self, 'docc', expected, doc_dir)

    def test_legacy_toctree_default(self):
        dataset = os.path.join(self.test_dir, 'dataset')
        expected = os.path.join(self.test_dir, 'expected-def')
        doc_dir = buildSphinx(dataset, config=self.config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doca', expected, doc_dir)
        assertExpectedWithOutput(self, 'docb', expected, doc_dir)
        assertExpectedWithOutput(self, 'docc', expected, doc_dir)

    def test_legacy_toctree_hidden(self):
        dataset = os.path.join(self.test_dir, 'dataset-hidden')
        expected = os.path.join(self.test_dir, 'expected-hidden')
        doc_dir = buildSphinx(dataset, config=self.config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)

    def test_legacy_toctree_numbered_default(self):
        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered-default')
        doc_dir = buildSphinx(dataset, config=self.config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc2', expected, doc_dir)

    def test_legacy_toctree_numbered_disable(self):
        config = dict(self.config)
        config['confluence_add_secnumbers'] = False

        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered-disabled')
        doc_dir = buildSphinx(dataset, config=config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc2', expected, doc_dir)

    def test_legacy_toctree_numbered_secnumbers_suffix(self):
        config = dict(self.config)
        config['confluence_secnumber_suffix'] = '!Z /+4'

        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered-suffix')
        doc_dir = buildSphinx(dataset, config=config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc2', expected, doc_dir)

    def test_legacy_toctree_numbered_secnumbers_depth(self):
        dataset = os.path.join(self.test_dir, 'dataset-numbered-depth')
        expected = os.path.join(self.test_dir, 'expected-numbered-depth')
        doc_dir = buildSphinx(dataset, config=self.config)

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc1', expected, doc_dir)
        assertExpectedWithOutput(self, 'doc2', expected, doc_dir)
