# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceStatus(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceStatus, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'status')

    @setup_builder('html')
    def test_html_confluence_status_role_ignore(self):
        # build attempt should not throw an exception/error
        self.build(self.dataset, relax=True)

    @setup_builder('confluence')
    def test_storage_confluence_status_role_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            statuses = data.find_all(
                'ac:structured-macro', {'ac:name': 'status'})
            self.assertEqual(len(statuses), 4)

            # ##########################################################
            # default
            # ##########################################################
            macro = statuses.pop(0)

            color = macro.find('ac:parameter', {'ac:name': 'color'})
            self.assertIsNotNone(color)
            self.assertEqual(color.text, '')

            title = macro.find('ac:parameter', {'ac:name': 'title'})
            self.assertIsNotNone(title)
            self.assertEqual(title.text, 'status a')

            subtle = macro.find('ac:parameter', {'ac:name': 'subtle'})
            self.assertIsNone(subtle)

            # ##########################################################
            # color
            # ##########################################################
            macro = statuses.pop(0)

            color = macro.find('ac:parameter', {'ac:name': 'color'})
            self.assertIsNotNone(color)
            self.assertEqual(color.text, 'yellow')

            title = macro.find('ac:parameter', {'ac:name': 'title'})
            self.assertIsNotNone(title)
            self.assertEqual(title.text, 'status b')

            subtle = macro.find('ac:parameter', {'ac:name': 'subtle'})
            self.assertIsNone(subtle)

            # ##########################################################
            # outlined
            # ##########################################################
            macro = statuses.pop(0)

            color = macro.find('ac:parameter', {'ac:name': 'color'})
            self.assertIsNotNone(color)
            self.assertEqual(color.text, '')

            title = macro.find('ac:parameter', {'ac:name': 'title'})
            self.assertIsNotNone(title)
            self.assertEqual(title.text, 'status c')

            subtle = macro.find('ac:parameter', {'ac:name': 'subtle'})
            self.assertIsNotNone(subtle)
            self.assertEqual(subtle.text, 'true')

            # ##########################################################
            # outlined, color
            # ##########################################################
            macro = statuses.pop(0)

            color = macro.find('ac:parameter', {'ac:name': 'color'})
            self.assertIsNotNone(color)
            self.assertEqual(color.text, 'green')

            title = macro.find('ac:parameter', {'ac:name': 'title'})
            self.assertIsNotNone(title)
            self.assertEqual(title.text, 'status d')

            subtle = macro.find('ac:parameter', {'ac:name': 'subtle'})
            self.assertIsNotNone(subtle)
            self.assertEqual(subtle.text, 'true')
