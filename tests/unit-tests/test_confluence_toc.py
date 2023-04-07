# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceToc(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'confluence-toc')

    @setup_builder('html')
    def test_html_confluence_toc_directive_ignore(self):
        # build attempt should not throw an exception/error
        self.build(self.dataset, relax=True)

    @setup_builder('confluence')
    def test_storage_confluence_toc_directive_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            tocs = data.find_all(
                'ac:structured-macro', {'ac:name': 'toc'})
            self.assertEqual(len(tocs), 2)

            # ##########################################################
            # basic
            # ##########################################################
            macro = tocs.pop(0)

            any_param = macro.find('ac:parameter')
            self.assertIsNone(any_param)

            # ##########################################################
            # options
            # ##########################################################
            macro = tocs.pop(0)

            type_ = macro.find('ac:parameter', {'ac:name': 'type'})
            self.assertIsNotNone(type_)
            self.assertEqual(type_.text, 'flat')

            absurl = macro.find('ac:parameter', {'ac:name': 'absoluteUrl'})
            self.assertIsNotNone(absurl)
            self.assertEqual(absurl.text, 'true')

            printable = macro.find('ac:parameter', {'ac:name': 'printable'})
            self.assertIsNotNone(printable)
            self.assertEqual(printable.text, 'false')
