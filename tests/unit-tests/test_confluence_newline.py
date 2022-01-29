# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceNewline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.dataset = os.path.join(test_dir, 'datasets', 'newline')

    def test_storage_confluence_newline_directive_expected(self):
        out_dir = build_sphinx(self.dataset, config=self.config)

        with parse('index', out_dir) as data:
            # expect three tags | p, br, p
            tags = data.find_all()
            self.assertEqual(len(tags), 3)

            para = tags[0]
            self.assertEqual(para.name, 'p')
            self.assertEqual(para.text, 'line1')

            para = tags[1]
            self.assertEqual(para.name, 'br')

            para = tags[2]
            self.assertEqual(para.name, 'p')
            self.assertEqual(para.text, 'line2')
