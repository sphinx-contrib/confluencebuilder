# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import prepare_conf
from tests.lib import prepare_sphinx
from tests.lib import prepare_sphinx_filenames
import os
import unittest


class TestConfluenceMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'common')
        cls.filenames = prepare_sphinx_filenames(cls.dataset,
            [
                'metadata',
            ],
            configs=[cls.config])

    def test_confluence_metadata_directive_expected(self):
        with prepare_sphinx(self.dataset, config=self.config) as app:
            app.build(filenames=self.filenames)
            builder_metadata = app.builder.metadata

            self.assertTrue(builder_metadata)
            self.assertTrue('metadata' in builder_metadata)
            doc_labels = builder_metadata['metadata']

            self.assertTrue(doc_labels)
            self.assertTrue('labels' in doc_labels)

            labels = doc_labels['labels']
            self.assertEqual(len(labels), 2)
            self.assertTrue('tag-a' in labels)
            self.assertTrue('tag-c' in labels)

    def test_confluence_metadata_directive_ignore(self):
        opts = {
            'builder': 'html',
            'config': self.config,
            'relax': True,
        }
        with prepare_sphinx(self.dataset, **opts) as app:
            # build attempt should not throw an exception/error
            app.build(filenames=self.filenames)
