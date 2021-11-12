# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceRstAdmonitions(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')
        self.filenames = [
            'admonitions',
        ]

    def test_storage_rst_admonitions(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=self.filenames)

        with parse('admonitions', out_dir) as data:
            self._verify_storage_tags(data, 'attention', 'note')
            self._verify_storage_tags(data, 'caution', 'note')
            self._verify_storage_tags(data, 'danger', 'warning')
            self._verify_storage_tags(data, 'error', 'warning')
            self._verify_storage_tags(data, 'hint', 'tip')
            self._verify_storage_tags(data, 'important', 'warning')
            self._verify_storage_tags(data, 'note', 'info')
            self._verify_storage_tags(data, 'tip', 'tip')
            self._verify_storage_tags(data, 'warning', 'warning')

            macro = self._verify_storage_tags(data, 'admonition', 'info')
            title_param = macro.find('ac:parameter', {'ac:name': 'title'})
            self.assertIsNotNone(title_param,
                'admonition is missing a title paramater')
            self.assertEqual(title_param.text, 'my-title',
                'admonition title value does not match expected')
            icon_param = macro.find('ac:parameter', {'ac:name': 'icon'})
            self.assertIsNotNone(icon_param,
                'admonition is missing a icon paramater')
            self.assertEqual(icon_param.text, 'false',
                'admonition icon value is not disabled')

    def _verify_storage_tags(self, data, text, expected_type):
        text += ' content'

        leaf = data.find(text=text)
        self.assertIsNotNone(leaf,
            'unable to find target admonition ' + text)

        expected_para = leaf.parent
        self.assertEqual(expected_para.name, 'p',
            'admonition ' + text + ' text not wrapped in a paragraph')

        expected_rich_txt_body = expected_para.parent
        self.assertEqual(expected_rich_txt_body.name, 'ac:rich-text-body',
            'admonition ' + text + ' context not using rich-text-body')

        expected_macro = expected_rich_txt_body.parent
        self.assertEqual(expected_macro.name, 'ac:structured-macro',
            'admonition ' + text + ' not contained inside a macro')

        self.assertEqual(expected_macro['ac:name'], expected_type,
            'admonition ' + text + ' not contained inside a macro')

        return expected_macro
