# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2020-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceSphinxProductionList(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'production-list')

    @setup_builder('confluence')
    def test_storage_sphinx_productionlist_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            container = data.find('pre')
            self.assertIsNotNone(container)
            self.assertTrue(container.text.strip())
