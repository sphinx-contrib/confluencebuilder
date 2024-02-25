# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceSphinxProductionList(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'production-list'

    @setup_builder('confluence')
    def test_storage_sphinx_productionlist_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            container = data.find('pre')
            self.assertIsNotNone(container)
            self.assertTrue(container.text.strip())
