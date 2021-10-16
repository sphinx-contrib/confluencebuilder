# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from tests.lib import EXT_NAME, prepare_conf, prepare_sphinx


class TestConfluenceExtension(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_extension_registration(self):
        mock_ds = os.path.join(self.test_dir, 'datasets', 'common')

        with prepare_sphinx(mock_ds, config=self.config) as app:
            if hasattr(app, 'extensions'):
                extensions = list(app.extensions.keys())
            else:
                extensions = list(app._extensions.keys())

            self.assertTrue(EXT_NAME in extensions)
