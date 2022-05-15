# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstMarkup(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceRstMarkup, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'rst', 'markup')

    @setup_builder('confluence')
    def test_storage_rst_markup(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            emphasis = data.find('em', text='emphasis')
            self.assertIsNotNone(emphasis)

            strong_emphasis = data.find('strong', text='strong emphasis')
            self.assertIsNotNone(strong_emphasis)

            interpreted = data.find('em', text='interpreted')
            self.assertIsNotNone(interpreted)

            inline = data.find('code', text='inline')
            self.assertIsNotNone(inline)

            subscript = data.find('sub', text='subscript')
            self.assertIsNotNone(subscript)

            superscript = data.find('sup', text='superscript')
            self.assertIsNotNone(superscript)

            ems = data.find_all('em')
            self.assertIsNotNone(len(ems), 3)
            guilabel = ems[-1]
            self.assertEqual(guilabel.text, 'guilabel')
            guilabel_hint = guilabel.find('u', text='g')
            self.assertIsNotNone(guilabel_hint)
