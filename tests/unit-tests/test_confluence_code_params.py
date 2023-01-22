# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2023 Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceCodeParams(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceCodeParams, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'code-block-params')

    @setup_builder('confluence')
    def test_storage_confluence_code_params_collapse(self):
        out_dir = self.build(self.dataset, filenames=['code-block-collapse'])

        with parse('code-block-collapse', out_dir) as data:
            code_macros = data.find_all('ac:structured-macro')
            self.assertIsNotNone(code_macros)
            self.assertEqual(len(code_macros), 2)

            for code_macro in code_macros:
                self.assertTrue(code_macro.has_attr('ac:name'))
                self.assertEqual(code_macro['ac:name'], 'code')

            # code macro with no collapse
            code_macro = code_macros.pop(0)

            collapse = code_macro.find('ac:parameter', {'ac:name': 'collapse'})
            self.assertIsNone(collapse)

            # code macro with collapse
            code_macro = code_macros.pop(0)

            collapse = code_macro.find('ac:parameter', {'ac:name': 'collapse'})
            self.assertIsNotNone(collapse)
            self.assertEqual(collapse.text, 'true')
