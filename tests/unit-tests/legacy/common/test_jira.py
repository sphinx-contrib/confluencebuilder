# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2019-2020 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from sphinx.errors import SphinxWarning
from tests.lib import assertExpectedWithOutput
from tests.lib import build_sphinx
from tests.lib import prepare_conf
from tests.lib import prepare_dirs
import os
import unittest

class TestConfluenceJira(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dataset_base = os.path.join(self.test_dir, 'dataset-jira')

        self.config = prepare_conf()
        self.config['confluence_jira_servers'] = {
            'test-jira-server': {
                'name': 'test-server-name',
                'id': '00000000-1234-0000-5678-000000000009',
            }
        }

        doc_dir = prepare_dirs('jira')
        self.doc_dir = doc_dir

    def test_legacy_jira(self):
        dataset = os.path.join(self.dataset_base, 'common')
        expected = os.path.join(self.test_dir, 'expected')

        build_sphinx(dataset, config=self.config, out_dir=self.doc_dir)
        assertExpectedWithOutput(
            self, 'jira', expected, self.doc_dir, tpn='index')

    def test_legacy_jira_bad_server_id(self):
        dataset = os.path.join(self.dataset_base, 'bad-sid')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config, out_dir=self.doc_dir)

    def test_legacy_jira_conflicting_server_id(self):
        dataset = os.path.join(self.dataset_base, 'conflicting-server-id')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config, out_dir=self.doc_dir)

    def test_legacy_jira_conflicting_server_name(self):
        dataset = os.path.join(self.dataset_base, 'conflicting-server-name')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config, out_dir=self.doc_dir)

    def test_legacy_jira_missing_server_id(self):
        dataset = os.path.join(self.dataset_base, 'missing-server-id')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config, out_dir=self.doc_dir)

    def test_legacy_jira_missing_server_name(self):
        dataset = os.path.join(self.dataset_base, 'missing-server-name')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config, out_dir=self.doc_dir)

    def test_legacy_jira_missing_server_entry(self):
        dataset = os.path.join(self.dataset_base, 'missing-server-entry')

        with self.assertRaises(SphinxWarning):
            build_sphinx(dataset, config=self.config, out_dir=self.doc_dir)