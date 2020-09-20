# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import assertExpectedWithOutput
from tests.lib import buildSphinx
from tests.lib import prepareConfiguration
from tests.lib import prepareDirectories
import os
import unittest

class TestConfluenceSinglePage(unittest.TestCase):
    def test_singlepage(self):
        config = prepareConfiguration()
        test_dir = os.path.dirname(os.path.realpath(__file__))

        dataset = os.path.join(test_dir, 'dataset')
        expected = os.path.join(test_dir, 'expected')
        doc_dir, doctree_dir = prepareDirectories('singlepage')
        buildSphinx(dataset, doc_dir, doctree_dir, config,
            builder='singleconfluence')

        assertExpectedWithOutput(self, 'index', expected, doc_dir)

    def test_singlepage_numbered(self):
        config = prepareConfiguration()
        test_dir = os.path.dirname(os.path.realpath(__file__))

        dataset = os.path.join(test_dir, 'dataset-numbered')
        expected = os.path.join(test_dir, 'expected-numbered')
        doc_dir, doctree_dir = prepareDirectories('singlepage-numbered')
        buildSphinx(dataset, doc_dir, doctree_dir, config,
            builder='singleconfluence')

        assertExpectedWithOutput(self, 'index', expected, doc_dir)
