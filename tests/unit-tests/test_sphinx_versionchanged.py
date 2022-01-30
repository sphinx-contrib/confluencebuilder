# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceSphinxVersionChanged(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceSphinxVersionChanged, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'common')
        cls.filenames = [
            'versionchanged',
        ]

    @setup_builder('confluence')
    def test_storage_sphinx_versionchanged_defaults(self):
        out_dir = self.build(self.dataset, filenames=self.filenames)

        with parse('versionchanged', out_dir) as data:
            note_macro = data.find('ac:structured-macro', {'ac:name': 'note'})
            self.assertIsNotNone(note_macro)

            rich_body = note_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            text_contents = rich_body.text.strip()
            self.assertIsNotNone(text_contents)
            self.assertTrue('5.6' in text_contents)
            self.assertTrue('versionchanged message' in text_contents)
