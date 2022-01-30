# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib import EXT_NAME
import os


class TestConfluenceExtension(ConfluenceTestCase):
    def test_extension_registration(self):
        mock_ds = os.path.join(self.datasets, 'common')

        with self.prepare(mock_ds) as app:
            if hasattr(app, 'extensions'):
                extensions = list(app.extensions.keys())
            else:
                extensions = list(app._extensions.keys())

            self.assertTrue(EXT_NAME in extensions)
