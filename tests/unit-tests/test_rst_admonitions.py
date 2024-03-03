# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib.testcase import setup_editor


class TestConfluenceRstAdmonitions(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = cls.datasets / 'rst' / 'admonitions'

    @setup_builder('confluence')
    def test_storage_rst_admonitions_default(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
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

    @setup_builder('confluence')
    @setup_editor('v2')
    def test_storage_rst_admonitions_v2(self):
        out_dir = self.build(self.dataset)

        with parse('index', out_dir) as data:
            self._verify_storage_tags(data, 'attention', 'note')
            self._verify_storage_tags(data, 'caution', 'note')
            self._verify_storage_tags(data, 'danger', 'warning')
            self._verify_storage_tags(data, 'error', 'warning')
            self._verify_storage_tags(data, 'hint', 'tip')
            self._verify_storage_tags(data, 'important', 'warning')
            self._verify_storage_tags(data, 'note', 'info')
            self._verify_storage_tags(data, 'tip', 'tip')
            self._verify_storage_tags(data, 'warning', 'warning')

            # v2 admonition is stored in a adf panel node
            # - adf nodes are wrapped in extension tags
            # - adf node should indicate that its a panel type
            # - inside the content should be the header and data
            adf_ext = data.find('ac:adf-extension', recursive=False)
            self.assertIsNotNone(adf_ext)

            adf_node = adf_ext.find('ac:adf-node', recursive=False)
            self.assertIsNotNone(adf_node)
            self.assertTrue(adf_node.has_attr('type'))
            self.assertEqual(adf_node['type'], 'panel')

            adf_attrib = adf_node.find('ac:adf-attribute', recursive=False)
            self.assertIsNotNone(adf_attrib)
            self.assertTrue(adf_attrib.has_attr('key'))
            self.assertEqual(adf_attrib['key'], 'panel-type')
            self.assertEqual(adf_attrib.text, 'note')

            adf_content = adf_node.find('ac:adf-content', recursive=False)
            self.assertIsNotNone(adf_content)

            header = adf_content.find('h3', recursive=False)
            self.assertIsNotNone(header)
            self.assertEqual(header.text, 'my-title',
                'admonition title value does not match expected')

            paragraph = adf_content.find('p', recursive=False)
            self.assertIsNotNone(paragraph)
            self.assertEqual(paragraph.text, 'admonition content',
                'admonition content does not match expected')

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
