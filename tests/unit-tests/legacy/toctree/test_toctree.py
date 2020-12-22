# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest

class TestConfluenceToctreeMarkup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_legacy_contents_default(self):
        dataset = os.path.join(self.test_dir, 'dataset-contents')
        doc_dir = build_sphinx(dataset, config=self.config)

        with parse('sub', doc_dir) as data:
            top_link = data.find('a')
            self.assertIsNotNone(top_link, 'unable to find first link tag (a)')
            self.assertEqual(top_link['href'], '#top',
                'contents root document not a top reference')

    def test_legacy_contents_with_title(self):
        config = dict(self.config)
        config['confluence_remove_title'] = False

        dataset = os.path.join(self.test_dir, 'dataset-contents')
        doc_dir = build_sphinx(dataset, config=config)

        with parse('sub', doc_dir) as data:
            top_link = data.find('ac:link')
            self.assertIsNotNone(top_link,
                'unable to find first link tag (ac:link)')
            self.assertEqual(top_link['ac:anchor'], '1. sub',
                'contents root document has an unexpected anchor value')
