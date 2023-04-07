# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from bs4 import CData
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceSphinxDownload(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'download')

    @setup_builder('confluence')
    def test_storage_sphinx_download_defaults(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            # view-file
            view_file_macro = data.find('ac:structured-macro',
                {'ac:name': 'view-file'})
            self.assertIsNotNone(view_file_macro)

            view_file_name = view_file_macro.find('ac:parameter',
                {'ac:name': 'name'})
            self.assertIsNotNone(view_file_name)

            attachment_ref = view_file_name.find('ri:attachment')
            self.assertIsNotNone(attachment_ref)
            self.assertTrue(attachment_ref.has_attr('ri:filename'))
            self.assertEqual(attachment_ref['ri:filename'], 'example.pdf')

            # link to file
            file_link = data.find('ac:link')
            self.assertIsNotNone(file_link)

            attachment_ref = file_link.find('ri:attachment')
            self.assertIsNotNone(attachment_ref)
            self.assertTrue(attachment_ref.has_attr('ri:filename'))
            self.assertEqual(attachment_ref['ri:filename'], 'example.pdf')

            link_body = file_link.find('ac:plain-text-link-body')
            self.assertIsNotNone(link_body)
            cdata_block = next(link_body.children, None)
            self.assertTrue(isinstance(cdata_block, CData))
            self.assertEqual(cdata_block, 'label')
