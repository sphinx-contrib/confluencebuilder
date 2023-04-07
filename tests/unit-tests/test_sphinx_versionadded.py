# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceSphinxVersionAdded(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'versionadded')

    @setup_builder('confluence')
    def test_storage_sphinx_versionadded_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            note_macro = data.find('ac:structured-macro', {'ac:name': 'info'})
            self.assertIsNotNone(note_macro)

            rich_body = note_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            text_contents = rich_body.text.strip()
            self.assertIsNotNone(text_contents)
            self.assertTrue('2.4' in text_contents)
            self.assertTrue('versionadded message' in text_contents)
