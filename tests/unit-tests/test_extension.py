# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib import EXT_NAME


class TestConfluenceExtension(ConfluenceTestCase):
    def test_extension_registration(self):
        mock_ds = self.datasets / 'common'

        with self.prepare(mock_ds) as app:
            self.assertTrue(EXT_NAME in app.extensions)
