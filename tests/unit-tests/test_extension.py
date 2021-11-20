# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import EXT_NAME
from tests.lib import prepare_conf
from tests.lib import prepare_sphinx
import os
import unittest


class TestConfluenceExtension(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = prepare_conf()
        cls.test_dir = os.path.dirname(os.path.realpath(__file__))

    def test_extension_registration(self):
        mock_ds = os.path.join(self.test_dir, 'datasets', 'common')

        with prepare_sphinx(mock_ds, config=self.config) as app:
            if hasattr(app, 'extensions'):
                extensions = list(app.extensions.keys())
            else:
                extensions = list(app._extensions.keys())

            self.assertTrue(EXT_NAME in extensions)
