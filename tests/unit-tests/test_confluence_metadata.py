# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import prepare_sphinx_filenames
import os


class TestConfluenceMetadata(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceMetadata, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'common')
        cls.filenames = prepare_sphinx_filenames(cls.dataset,
            [
                'metadata',
            ],
            configs=[cls.config])

    def test_confluence_metadata_directive_expected(self):
        with self.prepare(self.dataset) as app:
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

    @setup_builder('html')
    def test_html_confluence_metadata_directive_ignore(self):
        with self.prepare(self.dataset, relax=True) as app:
            # build attempt should not throw an exception/error
            app.build(filenames=self.filenames)
