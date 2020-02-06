# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2019-2020 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.
"""

from sphinxcontrib_confluencebuilder_util import ConfluenceTestUtil as _
from sphinx.errors import SphinxWarning
import os
import unittest

class TestConfluenceJira(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset_base = os.path.join(self.test_dir, 'dataset-jira')

        self.config = _.prepareConfiguration()
        self.config['confluence_jira_servers'] = {
            'test-jira-server': {
                'name': 'test-server-name',
                'id': '00000000-1234-0000-5678-000000000009',
            }
        }

        doc_dir, doctree_dir = _.prepareDirectories('jira')
        self.doc_dir = doc_dir
        self.doctree_dir = doctree_dir

    def test_jira(self):
        dataset = os.path.join(self.dataset_base, 'common')
        expected = os.path.join(self.test_dir, 'expected')

        _.buildSphinx(dataset, self.doc_dir, self.doctree_dir, self.config)
        _.assertExpectedWithOutput(
            self, 'jira', expected, self.doc_dir, tpn='index')

    def test_jira_bad_server_id(self):
        dataset = os.path.join(self.dataset_base, 'bad-sid')

        with self.assertRaises(SphinxWarning):
            _.buildSphinx(dataset, self.doc_dir, self.doctree_dir, self.config)

    def test_jira_conflicting_server_id(self):
        dataset = os.path.join(self.dataset_base, 'conflicting-server-id')

        with self.assertRaises(SphinxWarning):
            _.buildSphinx(dataset, self.doc_dir, self.doctree_dir, self.config)

    def test_jira_conflicting_server_name(self):
        dataset = os.path.join(self.dataset_base, 'conflicting-server-name')

        with self.assertRaises(SphinxWarning):
            _.buildSphinx(dataset, self.doc_dir, self.doctree_dir, self.config)

    def test_jira_missing_server_id(self):
        dataset = os.path.join(self.dataset_base, 'missing-server-id')

        with self.assertRaises(SphinxWarning):
            _.buildSphinx(dataset, self.doc_dir, self.doctree_dir, self.config)

    def test_jira_missing_server_name(self):
        dataset = os.path.join(self.dataset_base, 'missing-server-name')

        with self.assertRaises(SphinxWarning):
            _.buildSphinx(dataset, self.doc_dir, self.doctree_dir, self.config)

    def test_jira_missing_server_entry(self):
        dataset = os.path.join(self.dataset_base, 'missing-server-entry')

        with self.assertRaises(SphinxWarning):
            _.buildSphinx(dataset, self.doc_dir, self.doctree_dir, self.config)
