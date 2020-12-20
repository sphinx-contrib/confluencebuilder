# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import assertExpectedWithOutput
from tests.lib import buildSphinx
from tests.lib import parse
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
import os
import unittest

class TestConfluenceSinglePage(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepareConfiguration()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_legacy_singlepage_contents_default(self):
        dataset = os.path.join(self.test_dir, 'dataset-contents')
        doc_dir, doctree_dir = prepareDirectories()
        buildSphinx(dataset, doc_dir, doctree_dir, self.config,
            builder='singleconfluence')

        with parse('index', doc_dir) as data:
            links = data.find_all('ac:link')
            self.assertEqual(len(links), 3)
            self.assertEqual(links[0]['ac:anchor'], 'sub')
            self.assertEqual(links[1]['ac:anchor'], 'section')
            self.assertEqual(links[2]['ac:anchor'], 'section.1')

    def test_legacy_singlepage_contents_numbered(self):
        dataset = os.path.join(self.test_dir, 'dataset-contents-numbered')
        doc_dir, doctree_dir = prepareDirectories()
        buildSphinx(dataset, doc_dir, doctree_dir, self.config,
            builder='singleconfluence')

        with parse('index', doc_dir) as data:
            links = data.find_all('ac:link')
            self.assertEqual(len(links), 3)
            self.assertEqual(links[0]['ac:anchor'], '1. sub')
            self.assertEqual(links[1]['ac:anchor'], '1.1. section')
            self.assertEqual(links[2]['ac:anchor'], '1.2. section')

    def test_legacy_singlepage_default(self):
        dataset = os.path.join(self.test_dir, 'dataset')
        expected = os.path.join(self.test_dir, 'expected')
        doc_dir, doctree_dir = prepareDirectories()
        buildSphinx(dataset, doc_dir, doctree_dir, self.config,
            builder='singleconfluence')

        assertExpectedWithOutput(self, 'index', expected, doc_dir)

    def test_legacy_singlepage_numbered(self):
        dataset = os.path.join(self.test_dir, 'dataset-numbered')
        expected = os.path.join(self.test_dir, 'expected-numbered')
        doc_dir, doctree_dir = prepareDirectories()
        buildSphinx(dataset, doc_dir, doctree_dir, self.config,
            builder='singleconfluence')

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
