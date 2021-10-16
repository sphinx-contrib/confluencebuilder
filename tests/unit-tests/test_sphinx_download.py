# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

import os
import unittest

from bs4 import CData

from tests.lib import build_sphinx, parse, prepare_conf


class TestConfluenceSphinxDownload(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'download',
        ]

    def test_storage_sphinx_download_defaults(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('download', out_dir) as data:
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
