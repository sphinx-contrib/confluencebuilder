# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2020-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceMetadata(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceMetadata, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'metadata')

    def test_confluence_metadata_directive_expected(self):
        with self.prepare(self.dataset) as app:
            app.build()
            builder_metadata = app.builder.metadata

            self.assertTrue(builder_metadata)
            self.assertTrue('index' in builder_metadata)
            doc_labels = builder_metadata['index']

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
            app.build()
