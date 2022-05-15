# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstTransitions(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceRstTransitions, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'rst', 'transitions')

    @setup_builder('confluence')
    def test_storage_rst_transitions_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            hr = data.find('hr')
            self.assertIsNotNone(hr)
