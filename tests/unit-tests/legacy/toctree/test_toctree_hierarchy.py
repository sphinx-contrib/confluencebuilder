# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinxcontrib.confluencebuilder.state import ConfluenceState
from tests.lib import assertExpectedWithOutput
from tests.lib import build_sphinx
from tests.lib import prepare_conf
from tests.lib import prepare_dirs
import os
import unittest

class TestConfluenceToctreeHierarchyMarkup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        config = prepare_conf()
        config['confluence_max_doc_depth'] = 1
        config['confluence_page_hierarchy'] = True
        config['master_doc'] = 'toctree'

        test_dir = os.path.dirname(os.path.realpath(__file__))
        dataset = os.path.join(test_dir, 'dataset-hierarchy')
        self.expected = os.path.join(test_dir, 'expected-hierarchy')

        doc_dir = prepare_dirs('toctree-hierarchy')
        self.doc_dir = doc_dir

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def test_legacy_max_depth(self):
        assertExpectedWithOutput(
            self, 'toctree', self.expected, self.doc_dir)
        assertExpectedWithOutput(
            self, 'toctree-doc1', self.expected, self.doc_dir)
        assertExpectedWithOutput(
            self, 'toctree-doc2', self.expected, self.doc_dir)
        assertExpectedWithOutput(
            self, 'toctree-doc3', self.expected, self.doc_dir)

        test_paths = [
            os.path.join(self.doc_dir, 'toctree-doc2a.conf'),
            os.path.join(self.doc_dir, 'toctree-doc2aa.conf'),
            os.path.join(self.doc_dir, 'toctree-doc2aaa.conf'),
            os.path.join(self.doc_dir, 'toctree-doc2b.conf'),
            os.path.join(self.doc_dir, 'toctree-doc2c.conf')
        ]
        for test_path in test_paths:
            self.assertFalse(os.path.exists(test_path),
                'unexpected file was generated: {}'.format(test_path))

    def test_legacy_parent_registration(self):
        root_doc = ConfluenceState.parentDocname('toctree')
        self.assertIsNone(root_doc, 'root toctree has a parent')

        parent_doc = ConfluenceState.parentDocname('toctree-doc1')
        self.assertEqual(parent_doc, 'toctree',
            'toctree-doc1 parent is not root toctree')

        parent_doc = ConfluenceState.parentDocname('toctree-doc2')
        self.assertEqual(parent_doc, 'toctree',
            'toctree-doc2 parent is not root toctree')

        parent_doc = ConfluenceState.parentDocname('toctree-doc3')
        self.assertEqual(parent_doc, 'toctree',
            'toctree-doc3 parent is not root toctree')

        parent_doc = ConfluenceState.parentDocname('toctree-doc2a')
        self.assertEqual(parent_doc, 'toctree-doc2',
            'toctree-doc2a parent is not toctree-doc2')
