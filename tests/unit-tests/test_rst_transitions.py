# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder


class TestConfluenceRstTransitions(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'transitions'

    @setup_builder('confluence')
    def test_storage_rst_transitions_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            hr = data.find('hr')
            self.assertIsNotNone(hr)
