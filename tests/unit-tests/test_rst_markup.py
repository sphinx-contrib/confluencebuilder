# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest

class TestConfluenceRstMarkup(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'markup',
        ]

    def test_storage_rst_markup(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('markup', out_dir) as data:
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
