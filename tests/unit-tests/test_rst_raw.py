# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstRaw(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'rst', 'raw-storage')

    @setup_builder('confluence')
    def test_storage_rst_raw_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            strong = data.find('strong')
            self.assertIsNotNone(strong)
            self.assertEqual(strong.text, 'raw content')
