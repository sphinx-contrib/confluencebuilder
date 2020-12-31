# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest

class TestConfluenceSphinxVersionChanged(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'versionchanged',
        ]

    def test_storage_sphinx_versionchanged_defaults(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('versionchanged', out_dir) as data:
            note_macro = data.find('ac:structured-macro', {'ac:name': 'note'})
            self.assertIsNotNone(note_macro)

            rich_body = note_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            text_contents = rich_body.text.strip()
            self.assertIsNotNone(text_contents)
            self.assertTrue('5.6' in text_contents)
            self.assertTrue('versionchanged message' in text_contents)
