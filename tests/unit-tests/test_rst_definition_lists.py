# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceRstDefinitionLists(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'definition-lists',
        ]

    def test_storage_rst_definition_lists(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('definition-lists', out_dir) as data:
            def_list = data.find('dl')
            self.assertIsNotNone(def_list)

            def_list_tags = def_list.find_all(recursive=False)
            self.assertEqual(len(def_list_tags), 8)

            # term 1
            term = def_list_tags.pop(0)
            self.assertEqual(term.text, 'term 1')

            # definition 1
            definition = def_list_tags.pop(0)
            self.assertEqual(definition.text.strip(), 'definition 1')

            # term 2
            term = def_list_tags.pop(0)
            self.assertEqual(term.text, 'term 2')

            # definition 2
            definition = def_list_tags.pop(0)
            definition_paras = definition.find_all('p')
            self.assertEqual(len(definition_paras), 2)
            self.assertEqual(definition_paras[0].text,
                'definition 2, paragraph 1')
            self.assertEqual(definition_paras[1].text,
                'definition 2, paragraph 2')

            # term 3
            term = def_list_tags.pop(0)
            children = list(term.children)
            self.assertEqual(len(children), 2)
            self.assertEqual(children[0], 'term 3 : ')
            self.assertEqual(children[1].name, 'em')
            self.assertEqual(children[1].text, 'classifier')

            # definition 3
            definition = def_list_tags.pop(0)
            self.assertEqual(definition.text.strip(), 'definition 3')

            # term 4
            term = def_list_tags.pop(0)
            children = list(term.children)
            self.assertEqual(len(children), 4)
            self.assertEqual(children[0], 'term 4 : ')
            self.assertEqual(children[1].name, 'em')
            self.assertEqual(children[1].text, 'classifier one')
            self.assertEqual(children[2], ' : ')
            self.assertEqual(children[3].name, 'em')
            self.assertEqual(children[3].text, 'classifier two')

            # definition 4
            definition = def_list_tags.pop(0)
            self.assertEqual(definition.text.strip(), 'definition 4')
