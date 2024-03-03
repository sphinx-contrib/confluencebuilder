# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from pathlib import Path
from sphinx.util.docutils import NullReporter
from sphinxcontrib.confluencebuilder.translator import ConfluenceBaseTranslator
from tests.lib import prepare_conf
from tests.lib import prepare_sphinx
import unittest


class DummyDocument(dict):
    def __init__(self, source):
        self['source'] = str(source)
        self.reporter = NullReporter()


class TestConfluenceBaseTranslator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        cls.test_dir = Path(__file__).parent.resolve()

    def test_translator_docname_and_docparent(self):
        mock_ds = self.test_dir / 'datasets' / 'common'
        mock_docpath = mock_ds / 'foo' / 'bar' / 'baz.rst'
        doc = DummyDocument(mock_docpath)

        # prepare a dummy application; no need to actually build
        with prepare_sphinx(mock_ds, config=self.config) as app:
            translator = ConfluenceBaseTranslator(doc, app.builder)

        self.assertEqual(translator.docname, 'foo/bar/baz')
        self.assertEqual(translator.docparent.as_posix(), 'foo/bar')
