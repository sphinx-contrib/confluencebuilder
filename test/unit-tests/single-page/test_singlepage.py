# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2020 by the contributors (see AUTHORS file).
"""

from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
import os
import unittest

class TestConfluenceSinglePage(unittest.TestCase):
    def test_singlepage(self):
        config = _.prepareConfiguration()
        test_dir = os.path.dirname(os.path.realpath(__file__))

        dataset = os.path.join(test_dir, 'dataset')
        expected = os.path.join(test_dir, 'expected')
        doc_dir, doctree_dir = _.prepareDirectories('singlepage')
        _.buildSphinx(dataset, doc_dir, doctree_dir, config,
            builder='singleconfluence')

        _.assertExpectedWithOutput(self, 'index', expected, doc_dir)
