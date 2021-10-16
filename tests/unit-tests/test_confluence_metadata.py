# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import prepare_conf, prepare_sphinx, prepare_sphinx_filenames


class TestConfluenceMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, "datasets", "common")
        self.filenames = prepare_sphinx_filenames(
            self.dataset,
            [
                "metadata",
            ],
            configs=[self.config],
        )

    def test_confluence_metadata_directive(self):
        with prepare_sphinx(self.dataset, config=self.config) as app:
            app.build(filenames=self.filenames)
            builder_metadata = app.builder.metadata

            self.assertTrue(builder_metadata)
            self.assertTrue("metadata" in builder_metadata)
            doc_labels = builder_metadata["metadata"]

            self.assertTrue(doc_labels)
            self.assertTrue("labels" in doc_labels)

            labels = doc_labels["labels"]
            self.assertEqual(len(labels), 2)
            self.assertTrue("tag-a" in labels)
            self.assertTrue("tag-c" in labels)
