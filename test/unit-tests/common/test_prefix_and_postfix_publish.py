# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017-2019 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinxcontrib.confluencebuilder.state import ConfluenceState
from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
import os
import unittest


class TestBase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.specific_configs = {}

    def setUp(self):
        config = _.prepareConfiguration()
        for key, value in self.specific_configs.items():
            config[key] = value

        test_dir = os.path.dirname(os.path.realpath(__file__))
        dataset = os.path.join(test_dir, 'dataset-prefix-postfix')
        self.expected = os.path.join(test_dir, 'expected-prefix-postfix')

        doc_dir, doctree_dir = _.prepareDirectories('prefix-postfix')
        self.doc_dir = doc_dir

        _.buildSphinx(dataset, doc_dir, doctree_dir, config)

    def _check_pages_content(self):
        _.assertExpectedWithOutput(
            self, 'page1', self.expected, self.doc_dir)
        _.assertExpectedWithOutput(
            self, 'page2', self.expected, self.doc_dir)
        _.assertExpectedWithOutput(
            self, 'page3', self.expected, self.doc_dir)


class TestPrefix(TestBase):
    @classmethod
    def setUpClass(self):
        self.specific_configs = {}
        self.specific_configs['confluence_publish_prefix'] = 'prefix - '

    def test_prefix(self):
        _.assertExpectedWithOutput(
            self, 'index_prefix', self.expected, self.doc_dir, tpn='index')
        self._check_pages_content()


class TestPostfix(TestBase):
    @classmethod
    def setUpClass(self):
        self.specific_configs = {}
        self.specific_configs['confluence_publish_postfix'] = ' - postfix'

    def test_postfix(self):
        _.assertExpectedWithOutput(
            self, 'index_postfix', self.expected, self.doc_dir, tpn='index')
        self._check_pages_content()


class TestBothPrefixAndPostfix(TestBase):
    @classmethod
    def setUpClass(self):
        self.specific_configs = {}
        self.specific_configs['confluence_publish_prefix'] = 'prefix - '
        self.specific_configs['confluence_publish_postfix'] = ' - postfix'

    def test_both_prefix_and_postfix(self):
        _.assertExpectedWithOutput(
            self, 'index_both', self.expected, self.doc_dir, tpn='index')
        self._check_pages_content()
