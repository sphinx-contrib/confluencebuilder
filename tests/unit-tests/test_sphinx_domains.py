# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from pkg_resources import parse_version
from sphinx.__init__ import __version__ as sphinx_version
from sphinx.locale import _
from tests.lib import build_sphinx
from tests.lib import parse
from tests.lib import prepare_conf
import os
import unittest


class TestConfluenceSphinxDomains(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = prepare_conf()
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset = os.path.join(test_dir, 'datasets', 'common')

    def test_storage_sphinx_domain_c(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=['domains-c'])

        with parse('domains-c', out_dir) as data:
            definition = data.find('dl')
            self.assertIsNotNone(definition)

            # term
            term = definition.find('dt', recursive=False)
            self.assertIsNotNone(term)

            stronged_term = term.find('strong')
            self.assertIsNotNone(stronged_term)
            self.assertEqual(stronged_term.text, 'my_func')

            # ignore pre-v3.0 as it embeds asterisk in variable
            if parse_version(sphinx_version) >= parse_version('3.0'):
                param_context = term.find('em', text='context')
                self.assertIsNotNone(param_context)

            # description
            desc = definition.find('dd', recursive=False)
            self.assertIsNotNone(desc)
            self.assertEqual(desc.text, '')  # no description in this example

    def test_storage_sphinx_domain_cpp(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=['domains-cpp'])

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

    def test_storage_sphinx_domain_js(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=['domains-js'])

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

            # in sphinx v4.1+, exception are no longer strong styled
            if parse_version(sphinx_version) < parse_version('4.1'):
                expected_stronged.extend([
                    'SomeError',
                ])

            expected_stronged.extend([
                _('Returns') + ':',
            ])

            stronged = desc.find_all('strong')
            self.assertEqual(len(stronged), len(expected_stronged))

            for tag, expected in zip(stronged, expected_stronged):
                self.assertEqual(tag.text.strip(), expected)

    def test_storage_sphinx_domain_py(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=['domains-py'])

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

    def test_storage_sphinx_domain_rst(self):
        out_dir = build_sphinx(self.dataset, config=self.config,
            filenames=['domains-rst'])

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
