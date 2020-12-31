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

class TestConfluenceRstLists(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'lists',
        ]

    def test_storage_rst_lists(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('lists', out_dir) as data:
            root_tags = data.find_all(recursive=False)
            self.assertEqual(len(root_tags), 3)

            # ##########################################################
            # bullet list
            # ##########################################################
            bullet_list = root_tags.pop(0)
            self.assertEqual(bullet_list.name, 'ul')

            items = bullet_list.find_all('li', recursive=False)
            self.assertEqual(len(items), 4)

            self.assertEqual(items[0].text.strip(), 'first bullet')
            self.assertEqual(items[2].text.strip(), 'third item')
            self.assertEqual(items[3].text.strip(), 'forth item')

            complex_list = items[1]
            complex_tags = complex_list.find_all(recursive=False)

            self.assertEqual(complex_tags[0].name, 'p')
            self.assertEqual(complex_tags[0].text.strip(), 'second item')

            self.assertEqual(complex_tags[1].name, 'p')
            self.assertEqual(complex_tags[1].text.strip(),
                'second paragraph in the second item')

            self.assertEqual(complex_tags[2].name, 'p')
            self.assertEqual(complex_tags[2].text.strip(),
                'third paragraph in the second item')

            self.assertEqual(complex_tags[3].name, 'ul')
            sublist = complex_tags[3].find_all('li', recursive=False)
            self.assertEqual(len(sublist), 3)

            # ##########################################################
            # enumerated list
            # ##########################################################
            enumerated_list = root_tags.pop(0)
            self.assertEqual(enumerated_list.name, 'ol')

            css_style = 'list-style-type: decimal'
            self.assertTrue(enumerated_list.has_attr('style'))
            self.assertTrue(css_style in enumerated_list['style'])

            items = enumerated_list.find_all('li', recursive=False)
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0].text.strip(), 'enumerated a1')
            self.assertEqual(items[1].text.strip(), 'enumerated a2')

            # ##########################################################
            # enumerated list (styled)
            # ##########################################################
            enumerated_list = root_tags.pop(0)
            self.assertEqual(enumerated_list.name, 'ol')

            css_style = 'list-style-type: decimal'
            self.assertTrue(enumerated_list.has_attr('style'))
            self.assertTrue(css_style in enumerated_list['style'])

            items = enumerated_list.find_all('li', recursive=False)
            self.assertEqual(len(items), 4)

            css_style = 'list-style-type: lower-alpha'
            sublist1 = items[0].find('ol', recursive=False)
            self.assertIsNotNone(sublist1)
            self.assertTrue(sublist1.has_attr('style'))
            self.assertTrue(css_style in sublist1['style'])

            css_style = 'list-style-type: upper-alpha'
            sublist2 = items[1].find('ol', recursive=False)
            self.assertIsNotNone(sublist2)
            self.assertTrue(sublist2.has_attr('style'))
            self.assertTrue(css_style in sublist2['style'])

            css_style = 'list-style-type: decimal'
            sublist3 = items[2].find('ol', recursive=False)
            self.assertIsNotNone(sublist3)
            self.assertTrue(sublist3.has_attr('style'))
            self.assertTrue(css_style in sublist3['style'])

            css_style = 'list-style-type: lower-roman'
            sublist4 = items[3].find('ol', recursive=False)
            self.assertIsNotNone(sublist4)
            self.assertTrue(sublist4.has_attr('style'))
            self.assertTrue(css_style in sublist4['style'])
