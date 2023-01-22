# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2020-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceSphinxDeprecated(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceSphinxDeprecated, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'deprecated')

    @setup_builder('confluence')
    def test_storage_sphinx_deprecated_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            note_macro = data.find('ac:structured-macro', {'ac:name': 'note'})
            self.assertIsNotNone(note_macro)

            rich_body = note_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            text_contents = rich_body.text.strip()
            self.assertIsNotNone(text_contents)
            self.assertTrue('1.9' in text_contents)
            self.assertTrue('deprecated message' in text_contents)
