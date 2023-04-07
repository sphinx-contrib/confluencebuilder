# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceEmoticon(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
