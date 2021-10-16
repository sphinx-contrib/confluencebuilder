# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceRstRaw(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')

    def test_storage_rst_raw_default(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=['raw-storage'])

        with parse('raw-storage', out_dir) as data:
            strong = data.find('strong')
            self.assertIsNotNone(strong)
            self.assertEqual(strong.text, 'raw content')
