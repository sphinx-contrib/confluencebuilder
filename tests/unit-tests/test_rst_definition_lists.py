# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2020-2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstDefinitionLists(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceRstDefinitionLists, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'rst', 'definition-lists')

    @setup_builder('confluence')
    def test_storage_rst_definition_lists(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
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
