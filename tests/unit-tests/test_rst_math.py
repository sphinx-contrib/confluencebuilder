# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib.testcase import setup_editor
import shutil
import unittest


class TestConfluenceRstMath(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        # math images need latex to create
        if not shutil.which('latex'):
            msg = 'latex not installed'
            raise unittest.SkipTest(msg)

        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'math'

    @setup_builder('confluence')
    def test_storage_rst_math_v1_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            images = data.find_all('ac:image')
            self.assertIsNotNone(images)
            self.assertEqual(len(images), 1)

            # sanity check anchor creation
            anchor_tag = data.find('ac:structured-macro',
                {'ac:name': 'anchor'})
            self.assertIsNotNone(anchor_tag)
            anchor_param = anchor_tag.find('ac:parameter')
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'equation-euler')

    @setup_builder('confluence')
    @setup_editor('v2')
    def test_storage_rst_math_v2_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            images = data.find_all('ac:image')
            self.assertIsNotNone(images)
            self.assertEqual(len(images), 1)

            # sanity check anchor creation
            anchor_tag = data.find('ac:structured-macro',
                {'ac:name': 'anchor'})
            self.assertIsNotNone(anchor_tag)
            anchor_param = anchor_tag.find('ac:parameter')
            self.assertIsNotNone(anchor_param)
            self.assertEqual(anchor_param.text, 'equation-euler')
