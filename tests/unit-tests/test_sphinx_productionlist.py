# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceSphinxProductionList(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, "datasets", "common")
        self.filenames = [
            "production-list",
        ]

    def test_storage_sphinx_productionlist_defaults(self):
        out_dir = build_sphinx(
            self.dataset, config=self.config, filenames=self.filenames
        )

        with parse("production-list", out_dir) as data:
            container = data.find("pre")
            self.assertIsNotNone(container)
            self.assertTrue(container.text.strip())
