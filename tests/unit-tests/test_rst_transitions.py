# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceRstTransitions(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, "datasets", "common")
        self.filenames = [
            "transitions",
        ]

    def test_storage_rst_transitions_default(self):
        out_dir = build_sphinx(
            self.dataset, config=self.config, filenames=self.filenames
        )

        with parse("transitions", out_dir) as data:
            hr = data.find("hr")
            self.assertIsNotNone(hr)
