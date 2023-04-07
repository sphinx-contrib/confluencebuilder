# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from sphinx.locale import _
from tests.lib.parse import parse
from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
import os


class TestConfluenceSphinxDomains(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'domains')

    @setup_builder('confluence')
    def test_storage_sphinx_domain_c(self):
        out_dir = self.build(self.dataset, filenames=['domains-c'])

        with parse('domains-c', out_dir) as data:
            definition = data.find('dl')
            self.assertIsNotNone(definition)

            # term
            term = definition.find('dt', recursive=False)
            self.assertIsNotNone(term)

            stronged_term = term.find('strong')
            self.assertIsNotNone(stronged_term)
            self.assertEqual(stronged_term.text, 'my_func')

            param_context = term.find('em', text='context')
            self.assertIsNotNone(param_context)

            # description
            desc = definition.find('dd', recursive=False)
            self.assertIsNotNone(desc)
            self.assertEqual(desc.text, '')  # no description in this example

    @setup_builder('confluence')
    def test_storage_sphinx_domain_cpp(self):
        out_dir = self.build(self.dataset, filenames=['domains-cpp'])

        with parse('domains-cpp', out_dir) as data:
            definition = data.find('dl')
            self.assertIsNotNone(definition)

            # term
            term = definition.find('dt', recursive=False)
            self.assertIsNotNone(term)

            stronged_term = term.find('strong')
            self.assertIsNotNone(stronged_term)
            self.assertEqual(stronged_term.text, 'array')

            # description
            desc = definition.find('dd', recursive=False)
            self.assertIsNotNone(desc)
            self.assertEqual(desc.text, '')  # no description in this example

    @setup_builder('confluence')
    def test_storage_sphinx_domain_js(self):
        out_dir = self.build(self.dataset, filenames=['domains-js'])

        with parse('domains-js', out_dir) as data:
            definition = data.find('dl')
            self.assertIsNotNone(definition)

            # term
            term = definition.find('dt', recursive=False)
            self.assertIsNotNone(term)

            stronged_term = term.find('strong')
            self.assertIsNotNone(stronged_term)
            self.assertEqual(stronged_term.text, 'func')

            param_param1 = term.find('em', text='param1')
            self.assertIsNotNone(param_param1)

            param_param2 = term.find('em', text='param2')
            self.assertIsNotNone(param_param2)

            # description
            desc = definition.find('dd', recursive=False)
            self.assertIsNotNone(desc)

            expected_stronged = [
                _('Arguments') + ':',
                'param1',
                'param2',
                _('Throws') + ':',
            ]

            expected_stronged.extend([
                _('Returns') + ':',
            ])

            stronged = desc.find_all('strong')
            self.assertEqual(len(stronged), len(expected_stronged))

            for tag, expected in zip(stronged, expected_stronged):
                self.assertEqual(tag.text.strip(), expected)

    @setup_builder('confluence')
    def test_storage_sphinx_domain_py(self):
        out_dir = self.build(self.dataset, filenames=['domains-py'])

        with parse('domains-py', out_dir) as data:
            definition = data.find('dl')
            self.assertIsNotNone(definition)

            # term
            term = definition.find('dt', recursive=False)
            self.assertIsNotNone(term)

            stronged_term = term.find('strong')
            self.assertIsNotNone(stronged_term)
            self.assertEqual(stronged_term.text, 'repeat')

            # description
            desc = definition.find('dd', recursive=False)
            self.assertIsNotNone(desc)

    @setup_builder('confluence')
    def test_storage_sphinx_domain_rst(self):
        out_dir = self.build(self.dataset, filenames=['domains-rst'])

        with parse('domains-rst', out_dir) as data:
            definition = data.find('dl')
            self.assertIsNotNone(definition)

            # term
            term = definition.find('dt', recursive=False)
            self.assertIsNotNone(term)

            stronged_term = term.find('strong')
            self.assertIsNotNone(stronged_term)
            self.assertEqual(stronged_term.text, '.. directive::')

            # description
            desc = definition.find('dd', recursive=False)
            self.assertIsNotNone(desc)
            self.assertEqual(desc.text.strip(), 'desc')
