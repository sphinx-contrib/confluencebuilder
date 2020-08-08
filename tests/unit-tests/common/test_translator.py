# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from collections import namedtuple
from sphinxcontrib.confluencebuilder.translator import ConfluenceBaseTranslator
from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
from sphinxcontrib_confluencebuilder_util import EXT_NAME
import os
import unittest

Reporter = namedtuple('Reporter', 'warning')

class DummyDocument(dict):
    def __init__(self, source, warn=False):
        self['source'] = source
        self.reporter = Reporter(warn)

class TestConfluenceBaseTranslator(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = _.prepareConfiguration()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_docname_and_docparent(self):
        mock_ds = os.path.join(self.test_dir, 'dataset-common')
        doc_dir, doctree_dir = _.prepareDirectories('config-dummy')
        mock_docpath = os.path.join(mock_ds, 'foo', 'bar' , 'baz.rst')
        doc = DummyDocument(mock_docpath)

        # prepare a dummy application; no need to actually build
        with _.prepareSphinx(mock_ds, doc_dir, doctree_dir, self.config) as app:
            translator = ConfluenceBaseTranslator(doc, app.builder)

        self.assertEqual(translator.docname, 'foo/bar/baz')
        self.assertEqual(translator.docparent, 'foo/bar/')
