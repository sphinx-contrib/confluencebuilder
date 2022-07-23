# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceEmoticon(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceEmoticon, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'emoticon')

    @setup_builder('html')
    def test_html_confluence_emoticon_role_ignore(self):
        # build attempt should not throw an exception/error
        self.build(self.dataset, relax=True)

    @setup_builder('confluence')
    def test_storage_confluence_emoticon_role_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            emoticons = data.find_all('ac:emoticon')
            self.assertEqual(len(emoticons), 1)

            # ##########################################################
            # default
            # ##########################################################
            macro = emoticons.pop(0)

            self.assertTrue(macro.has_attr('ac:name'))
            self.assertEqual(macro['ac:name'], 'tick')
