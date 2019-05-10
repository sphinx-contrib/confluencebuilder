# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2016-2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

import os
from collections import namedtuple

import unittest

from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil, EXT_NAME
from sphinxcontrib.confluencebuilder.translator import ConfluenceTranslator

Reporter = namedtuple('Reporter', 'warning')

class DummyDocument(dict):
    def __init__(self, source, warn=False):
        self['source'] = source
        self.reporter = Reporter(warn)

class TestConfluenceTranslator(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # prepare a dummy application; no need to actually build
        self.config = { 'extensions': EXT_NAME }
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.mock_ds = os.path.join(self.test_dir, 'dataset-common')
        self.doc_dir, self.doctree_dir = ConfluenceTestUtil.prepareDirectories('config-dummy')

    def test_docname_and_docparent(self):
        with ConfluenceTestUtil.prepareSphinx(self.mock_ds, self.doc_dir, self.doctree_dir, self.config) as app:
            translator = ConfluenceTranslator(DummyDocument(os.path.join(self.mock_ds, 'foo', 'bar' , 'baz.rst')), app.builder)

        self.assertEqual(translator.docname, 'foo/bar/baz')
        self.assertEqual(translator.docparent, 'foo/bar/')
