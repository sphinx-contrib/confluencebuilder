# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceMetadata(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'metadata'

    def test_confluence_metadata_directive_expected(self):
        with self.prepare(self.dataset) as app:
            app.build()
            builder_metadata = app.builder.metadata

            self.assertTrue(builder_metadata)
            self.assertTrue('index' in builder_metadata)

            doc_metadata = builder_metadata['index']
            self.assertTrue(doc_metadata)

            # verify expected editor override
            self.assertTrue('editor' in doc_metadata)
            editor = doc_metadata['editor']
            self.assertEqual(editor, 'v2')

            # verify expected full-width override
            self.assertTrue('fullWidth' in doc_metadata)
            editor = doc_metadata['fullWidth']
            self.assertEqual(editor, 'true')

            # verify expected labels
            self.assertTrue('labels' in doc_metadata)
            labels = doc_metadata['labels']
            self.assertEqual(len(labels), 2)
            self.assertIn('tag-a', labels)
            self.assertIn('tag-c', labels)

    @setup_builder('html')
    def test_html_confluence_metadata_directive_ignore(self):
        with self.prepare(self.dataset, relax=True) as app:
            # build attempt should not throw an exception/error
            app.build()
