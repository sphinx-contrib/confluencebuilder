# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from collections import namedtuple
from sphinxcontrib.confluencebuilder.translator import ConfluenceBaseTranslator
from tests.lib import prepare_conf
from tests.lib import prepare_sphinx
import os
import unittest

Reporter = namedtuple('Reporter', 'warning')


class DummyDocument(dict):
    def __init__(self, source, warn=False):
        self['source'] = source
        self.reporter = Reporter(warn)


class TestConfluenceBaseTranslator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        cls.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_translator_docname_and_docparent(self):
        mock_ds = os.path.join(self.test_dir, 'datasets', 'common')
        mock_docpath = os.path.join(mock_ds, 'foo', 'bar', 'baz.rst')
        doc = DummyDocument(mock_docpath)

        # prepare a dummy application; no need to actually build
        with prepare_sphinx(mock_ds, config=self.config) as app:
            translator = ConfluenceBaseTranslator(doc, app.builder)

        self.assertEqual(translator.docname, 'foo/bar/baz')
        self.assertEqual(translator.docparent, 'foo/bar/')
